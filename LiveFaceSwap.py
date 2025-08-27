import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import imutils

# Initialize Mediapipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

def get_landmarks(image):
    h, w, _ = image.shape
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if results.multi_face_landmarks:
        return np.array([
            (int(p.x * w), int(p.y * h)) 
            for p in results.multi_face_landmarks[0].landmark
        ])
    return None

def triangulation(img, points):
    rect = cv2.boundingRect(np.array(points))
    subdiv = cv2.Subdiv2D(rect)
    for p in points:
        subdiv.insert((int(p[0]), int(p[1])))
    triangles = subdiv.getTriangleList()
    triangle_indices = []
    for t in triangles:
        pts = [(int(t[0]), int(t[1])), (int(t[2]), int(t[3])), (int(t[4]), int(t[5]))]
        idx = []
        for p in pts:
            for i, pt in enumerate(points):
                if abs(p[0] - pt[0]) < 1 and abs(p[1] - pt[1]) < 1:
                    idx.append(i)
                    break
        if len(idx) == 3:
            triangle_indices.append(tuple(idx))
    return triangle_indices

def warp_triangle(src, dst, src_tri, dst_tri):
    src_rect = cv2.boundingRect(np.float32([src_tri]))
    dst_rect = cv2.boundingRect(np.float32([dst_tri]))

    src_crop = src[src_rect[1]:src_rect[1]+src_rect[3], src_rect[0]:src_rect[0]+src_rect[2]]
    dst_crop_shape = (dst_rect[2], dst_rect[3])

    src_tri_offset = [(p[0]-src_rect[0], p[1]-src_rect[1]) for p in src_tri]
    dst_tri_offset = [(p[0]-dst_rect[0], p[1]-dst_rect[1]) for p in dst_tri]

    warp_mat = cv2.getAffineTransform(np.float32(src_tri_offset), np.float32(dst_tri_offset))
    warped = cv2.warpAffine(src_crop, warp_mat, dst_crop_shape, borderMode=cv2.BORDER_REFLECT_101)

    mask = np.zeros((dst_rect[3], dst_rect[2], 3), dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(dst_tri_offset), (1, 1, 1), 16, 0)

    dst_patch = dst[dst_rect[1]:dst_rect[1]+dst_rect[3], dst_rect[0]:dst_rect[0]+dst_rect[2]]
    dst_patch = dst_patch * (1 - mask) + warped * mask
    dst[dst_rect[1]:dst_rect[1]+dst_rect[3], dst_rect[0]:dst_rect[0]+dst_rect[2]] = dst_patch

def swap_faces(src_img, dst_img):
    src_img = imutils.resize(src_img, width=500)
    dst_img = imutils.resize(dst_img, width=500)

    landmarks1 = get_landmarks(src_img)
    landmarks2 = get_landmarks(dst_img)

    if landmarks1 is None or landmarks2 is None:
        return None

    triangles = triangulation(src_img, landmarks1)

    dst_warped = dst_img.copy()
    for tri in triangles:
        tri1 = [landmarks1[i] for i in tri]
        tri2 = [landmarks2[i] for i in tri]
        warp_triangle(src_img, dst_warped, tri1, tri2)

    mask = np.zeros_like(dst_img)
    hull = cv2.convexHull(np.array(landmarks2))
    cv2.fillConvexPoly(mask, hull, (255, 255, 255))
    r = cv2.boundingRect(hull)
    center = (r[0] + r[2] // 2, r[1] + r[3] // 2)

    output = cv2.seamlessClone(dst_warped, dst_img, mask, center, cv2.NORMAL_CLONE)
    return output

# Streamlit UI
st.set_page_config(page_title="Live Face Swap App", layout="centered")
st.title("Live Face Swap App")
st.markdown("📸 Capture two images (source + target) and swap faces instantly!")

# Step 1: Capture source image
st.subheader("Step 1: Capture Source Face")
source_img = st.camera_input("Take photo of your face")

# Step 2: Capture target image
st.subheader("Step 2: Capture Target Face")
target_img = st.camera_input("Take photo of target face")

if source_img and target_img:
    # Convert to OpenCV format
    source_cv = cv2.cvtColor(np.array(Image.open(source_img).convert("RGB")), cv2.COLOR_RGB2BGR)
    target_cv = cv2.cvtColor(np.array(Image.open(target_img).convert("RGB")), cv2.COLOR_RGB2BGR)

    with st.spinner("Swapping faces..."):
        output = swap_faces(source_cv, target_cv)

    if output is not None:
        st.success("✅ Face Swap Complete!")
        st.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB), caption="Swapped Output", use_column_width=True)
    else:
        st.error("❌ Could not detect faces. Try again with clearer images.")
