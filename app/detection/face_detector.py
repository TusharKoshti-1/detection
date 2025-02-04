import cv2
import mediapipe as mp
import numpy as np

class FaceMeshDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

    def process_frame(self, frame):
        if frame is None:
            return None, None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = np.array([[lm.x, lm.y] for lm in results.multi_face_landmarks[0].landmark])
            ear = self._calculate_ear(landmarks)
            return ear, landmarks
        return None, None

    def _calculate_ear(self, landmarks):
        def _eye_aspect_ratio(eye_indices):
            return (
                np.linalg.norm(landmarks[eye_indices[1]] - landmarks[eye_indices[5]]) +
                np.linalg.norm(landmarks[eye_indices[2]] - landmarks[eye_indices[4]])
            ) / (2 * np.linalg.norm(landmarks[eye_indices[0]] - landmarks[eye_indices[3]]))
        
        return (_eye_aspect_ratio(self.LEFT_EYE_INDICES) + 
                _eye_aspect_ratio(self.RIGHT_EYE_INDICES)) / 2

    def draw_landmarks(self, frame, landmarks, ear=None, threshold=0.3):
        # Determine the color: green if eyes are open, red if eyes are closed.
        color = (0, 255, 0)  # default green
        if ear is not None and ear < threshold:
            color = (0, 0, 255)  # red if eyes are closed

        # Draw circles on each eye landmark.
        for idx in self.LEFT_EYE_INDICES + self.RIGHT_EYE_INDICES:
            x = int(landmarks[idx][0] * frame.shape[1])
            y = int(landmarks[idx][1] * frame.shape[0])
            cv2.circle(frame, (x, y), 2, color, -1)

        # Compute bounding box around both eyes.
        points = [
            (int(landmarks[i][0] * frame.shape[1]), int(landmarks[i][1] * frame.shape[0]))
            for i in self.LEFT_EYE_INDICES + self.RIGHT_EYE_INDICES
        ]
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        # Draw the bounding box.
        cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), color, 2)

        return frame
