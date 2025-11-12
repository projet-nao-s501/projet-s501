# 🔥 Option 5 : Scan Vertical avec Corps Penché EN ARRIÈRE

## 🎯 Objectif

Permettre au robot NAO de regarder **très haut** (jusqu'au plafond) en utilisant **tout son corps** :
- **Bras vers l'avant** : Contrepoids pour l'équilibre
- **Corps penché EN ARRIÈRE** : Permet de regarder beaucoup plus haut que la tête seule

---

## ⚙️ Principe Technique

### 1. Pourquoi pencher le corps EN ARRIÈRE ?

```
SANS corps penché (Option 4):
  Limite HeadPitch = -0.45 rad (~26°)
  Vision verticale = 26°

AVEC corps penché (Option 5):
  HeadPitch = -0.60 rad (~34°)
  Corps penché = +15° supplémentaires
  Vision verticale totale ≈ 49° !
```

### 2. Articulations utilisées

| Articulation | Angle | Effet |
|--------------|-------|-------|
| **KneePitch** | -0.10 rad | Genoux légèrement pliés vers l'arrière |
| **HipPitch** | +0.15 rad | Bassin/Hanches penchées EN ARRIÈRE |
| **ShoulderPitch** | 0.6 rad | Bras vers l'avant (contrepoids) |
| **HeadPitch** | -0.60 rad | Tête regarde vers le haut |

---

## 📋 Séquence d'Exécution

### PHASE 1 : Préparation (~4 secondes)

1. **Activation des moteurs** (0.8s)
   ```python
   motion.setStiffnesses(["Head", "LArm", "RArm", "LLeg", "RLeg"], 1.0)
   ```

2. **Bras vers l'avant** (1.5s)
   ```python
   ShoulderPitch = 0.6 rad (vers l'avant)
   ShoulderRoll = ±0.15 rad (légèrement écartés)
   ```
   → Crée un contrepoids pour stabiliser

3. **Corps penché EN ARRIÈRE** (2s)
   ```python
   # Étape 1: Genoux
   KneePitch = -0.10 rad (genoux vers l'arrière)
   
   # Étape 2: Bassin
   HipPitch = +0.15 rad (bassin penché en arrière)
   ```
   → Le robot se penche en arrière, centre de gravité compensé par les bras

### PHASE 2 : Scan Vertical (16 secondes)

4 positions, 4 secondes chacune :

| Cran | Nom | HeadPitch | Angle effectif |
|------|-----|-----------|----------------|
| 1 | Genoux | +0.20 rad | ~11° (bas) |
| 2 | Torse | -0.10 rad | ~-6° (centre) |
| 3 | Poitrine | -0.35 rad | ~-20° (haut) |
| 4 | **PLAFOND** | **-0.60 rad** | **~49°** (très haut !) |

### PHASE 3 : Retour Normal (~6 secondes)

1. **Tête au centre** (1s)
   ```python
   HeadPitch = 0.0
   ```

2. **Corps droit** (2.5s)
   ```python
   KneePitch = 0.0 (genoux droits)
   HipPitch = 0.0 (bassin droit)
   ```

3. **Bras le long du corps** (2s)
   ```python
   ShoulderPitch = 1.5 rad (position repos)
   ```

---

## 🔬 Différences avec la version précédente

### ❌ Ancienne version (qui ne marchait pas)
- Utilisait `setAngles()` sans attendre
- Bras trop en avant (0.5 rad, trop agressif)
- HipPitch trop élevé (0.20 rad, instable)
- Pas de contrôle des genoux

### ✅ Nouvelle version (corrigée)
- Utilise `angleInterpolationWithSpeed()` (mouvement fluide)
- Bras modérés (0.6 rad, stable)
- HipPitch raisonnable (0.15 rad)
- **Contrôle des genoux** (KneePitch = -0.10) pour pencher le corps
- Gestion d'erreur améliorée avec remise en sécurité

---

## ⚠️ Sécurité

### Avant de lancer :
- ✅ Robot en position DEBOUT (option 1)
- ✅ Surface plane et stable
- ✅ Espace libre autour (1m minimum)
- ✅ Batteries chargées (>30%)

### Pendant l'exécution :
- 👁️ Surveiller l'équilibre du robot
- 🚫 Ne pas toucher le robot
- ⚡ En cas de vacillement : Ctrl+C pour arrêter

### En cas de problème :
Le script inclut une **remise en sécurité automatique** :
```python
except Exception as e:
    # Tentative de sécurisation
    - Tête au centre
    - Genoux droits
    - Bassin droit
```

---

## 🧪 Comment tester

### Test isolé :
```powershell
cd C:\Nao\projet-s501
python test_scan_option5.py
```

### Dans le menu :
```powershell
python nao_menu_simple.py
# Option 1: Debout
# Option 5: Scan avec corps penché
```

---

## 📊 Résultats attendus

| Métrique | Valeur |
|----------|--------|
| Durée totale | ~26 secondes |
| Angle max atteint | 49° (vision verticale) |
| Stabilité | ⭐⭐⭐⭐ Bonne |
| Consommation batterie | Moyenne-Haute |

---

## 💡 Conseils d'utilisation

### Pour une démonstration :
1. Faire d'abord l'option 4 (scan simple)
2. Expliquer la différence
3. Lancer l'option 5
4. Montrer la différence d'angle

### Pour un scan de sécurité :
- Utiliser option 4 pour scan rapide quotidien
- Utiliser option 5 pour scan complet approfondi

---

## 🔧 Paramètres ajustables

Si vous voulez modifier le comportement :

```python
# Ligne 353-354: Bras
ShoulderPitch = 0.6  # Plus petit = bras plus hauts (moins stable)
                      # Plus grand = bras plus bas (plus stable)

# Ligne 360: Genoux
KneePitch = -0.10  # Plus négatif = plus penché (risque)
                    # Moins négatif = moins penché (sûr)

# Ligne 362: Bassin
HipPitch = 0.15  # Plus grand = plus penché (risque)
                  # Plus petit = moins penché (sûr)

# Ligne 372: Angle max tête
HeadPitch = -0.60  # Plus négatif = regarde plus haut (limite -0.67)
```

---

## 📞 Dépannage

### "Le robot vacille"
→ Réduire HipPitch à 0.10

### "Le robot ne regarde pas assez haut"
→ Augmenter progressivement HeadPitch jusqu'à -0.67 max

### "Erreur lors de l'exécution"
→ Vérifier que le robot est debout
→ Vérifier les batteries
→ Relancer le robot

### "Le robot ne revient pas en position normale"
→ Utiliser l'option 8 (Reset)
→ Ou redémarrer le robot

---

**Version** : 2025-10-06  
**Status** : ✅ Testé et fonctionnel
