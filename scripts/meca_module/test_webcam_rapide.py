#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""
Script de test rapide pour vérifier si la webcam fonctionne
"""

import cv2
import sys

print("=== Test Webcam Rapide ===\n")

# Vérifier si OpenCV est installé
try:
    print(f"✓ OpenCV version: {cv2.__version__}")
except:
    print("✗ OpenCV non disponible")
    print("  Installez avec: pip install opencv-python")
    sys.exit(1)

# Tester l'ouverture de la webcam
print("\nTest d'ouverture de la webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("✗ ÉCHEC: Impossible d'ouvrir la webcam")
    print("\nRaisons possibles:")
    print("  1. Aucune webcam n'est connectée")
    print("  2. La webcam est utilisée par un autre programme")
    print("  3. Les permissions d'accès sont bloquées")
    sys.exit(1)

print("✓ Webcam ouverte avec succès!")

# Obtenir les informations de la webcam
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"\nInformations de la webcam:")
print(f"  Résolution: {width}x{height}")
print(f"  FPS: {fps}")

# Tester la capture d'une image
print("\nTest de capture d'image...")
ret, frame = cap.read()

if ret:
    print("✓ Capture d'image réussie!")
    print(f"  Dimensions de l'image: {frame.shape}")
    
    # Sauvegarder une image de test
    cv2.imwrite("test_webcam_capture.jpg", frame)
    print("  📸 Image test sauvegardée: test_webcam_capture.jpg")
    
    # Afficher l'image pendant 3 secondes
    print("\nAffichage de la fenêtre pendant 3 secondes...")
    cv2.imshow("Test Webcam", frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    
    print("\n✓ TEST RÉUSSI: La webcam fonctionne correctement!")
    print("  Vous pouvez utiliser l'option 3 du menu NAO.")
else:
    print("✗ ÉCHEC: Impossible de capturer une image")

cap.release()
print("\nTest terminé.")
