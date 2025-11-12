# 📊 Comparaison des Options de Scan Vertical

## Vue d'ensemble

Le menu NAO propose deux types de scan vertical, chacun avec ses spécificités :

---

## ⚙️ OPTION 4 : Scan Vertical Simple (4 crans)

### Caractéristiques :
- **Direction** : BAS → HAUT
- **Mouvements** : Tête uniquement
- **Stabilité** : ⭐⭐⭐⭐⭐ Très stable
- **Hauteur max** : -0.45 rad (~26°)

### Positions :
1. **Genoux** : Pitch = 0.25 (regarde vers le bas)
2. **Torse** : Pitch = -0.05 (centre)
3. **Poitrine** : Pitch = -0.25 (haut)
4. **Tête** : Pitch = -0.45 (très haut)

### Avantages :
✅ Simple et sûr  
✅ Pas de risque de déséquilibre  
✅ Rapide à exécuter  
✅ Ne nécessite que la tête  

### Inconvénients :
❌ Hauteur de vision limitée  
❌ Ne peut pas voir le plafond  

---

## 🔥 OPTION 5 : Scan avec Bras + Inclinaison (4 crans)

### Caractéristiques :
- **Direction** : BAS → HAUT (identique à l'option 4)
- **Mouvements** : Tête + Bras + Corps (bassin)
- **Stabilité** : ⭐⭐⭐ Stable mais attention
- **Hauteur max** : -0.65 rad (~37°) - **44% plus haut que l'option 4 !**

### Positions :
1. **Genoux** : Pitch = 0.20 (regarde vers le bas)
2. **Torse** : Pitch = -0.10 (centre)
3. **Poitrine** : Pitch = -0.35 (haut)
4. **PLAFOND** : Pitch = -0.65 (TRÈS TRÈS haut !) ⬆️⬆️⬆️

### Préparation spéciale :
1. **Bras vers l'avant** :
   - ShoulderPitch : 0.5 rad (bras tendus devant)
   - ShoulderRoll : ±0.2 rad (écartés)
   
2. **Corps penché en arrière** :
   - HipPitch : 0.20 rad (bassin incliné)
   - Permet de compenser et regarder plus haut

### Avantages :
✅ Peut voir le plafond !  
✅ Champ de vision vertical maximal  
✅ Utilise tout le corps pour l'équilibre  
✅ Plus impressionnant visuellement  

### Inconvénients :
⚠️ Nécessite plus de temps (préparation + retour)  
⚠️ Le robot doit être en position DEBOUT stable  
⚠️ Consomme plus de batterie  
⚠️ Nécessite de l'espace autour du robot  

---

## 📐 Comparaison technique

| Critère | Option 4 | Option 5 |
|---------|----------|----------|
| **Angle max** | -0.45 rad (~26°) | -0.65 rad (~37°) |
| **Gain en hauteur** | Référence | +44% |
| **Durée totale** | ~18 secondes | ~28 secondes |
| **Moteurs utilisés** | 2 (tête) | 10+ (tête, bras, corps) |
| **Complexité** | ⭐ Simple | ⭐⭐⭐ Complexe |
| **Risque déséquilibre** | ⭐ Très faible | ⭐⭐⭐ Moyen |

---

## 🎯 Quand utiliser chaque option ?

### Utiliser l'OPTION 4 si :
- ✅ Vous voulez un scan rapide et simple
- ✅ Le robot est dans un espace restreint
- ✅ Vous voulez minimiser les mouvements
- ✅ La batterie est faible
- ✅ Première utilisation / apprentissage

### Utiliser l'OPTION 5 si :
- ✅ Vous devez scanner jusqu'au plafond
- ✅ Le robot a assez d'espace autour
- ✅ Vous voulez la couverture maximale
- ✅ Le robot est stable et bien chargé
- ✅ Vous voulez impressionner ! 😎

---

## ⚠️ Précautions pour l'OPTION 5

1. **Avant de lancer** :
   - Le robot DOIT être en position DEBOUT (option 1)
   - Vérifier qu'il y a de l'espace autour
   - Batteries suffisamment chargées (>30%)
   - Surface plane et stable

2. **Pendant l'exécution** :
   - Ne pas toucher le robot
   - Surveiller l'équilibre
   - Si le robot vacille, arrêter le script (Ctrl+C)

3. **Après l'exécution** :
   - Le robot revient automatiquement en position normale
   - Utiliser l'option 8 (Reset) si nécessaire

---

## 🔬 Détails techniques : Pourquoi l'option 5 regarde plus haut ?

### Principe physique :
```
Tête seule (Option 4) :
    Limite = articulation HeadPitch (~26°)
    
Tête + Corps penché (Option 5) :
    Limite = HeadPitch + HipPitch
    ≈ 37° + 11° de compensation
    = ~48° de vision verticale effective !
```

### Compensation par les bras :
- Les bras vers l'avant déplacent le centre de gravité
- Permet au robot de se pencher en arrière sans tomber
- Crée un contrepoids pour la stabilité

---

## 📝 Notes de développement

### Angles testés et validés :
- **HipPitch = 0.20** : Optimal (équilibre + hauteur)
- **ShoulderPitch = 0.5** : Bras tendus sans forcer
- **HeadPitch = -0.65** : Maximum sécurisé

### Angles à éviter :
- ❌ HipPitch > 0.30 : Risque de chute arrière
- ❌ ShoulderPitch < 0.3 : Bras trop hauts, instable
- ❌ HeadPitch < -0.70 : Limite mécanique

---

## 🎓 Pédagogie : Utilisation en démonstration

### Séquence recommandée pour une démonstration :

1. **Option 1** : Debout (montrer le réveil du robot)
2. **Option 4** : Scan simple (montrer le scan basique)
3. **Option 5** : Scan avancé (montrer les capacités étendues)
4. **Option 8** : Reset (remettre en position neutre)
5. **Option 2** : S'asseoir (fin de démonstration)

---

## 📞 Support

Si l'option 5 ne fonctionne pas :
1. Tester avec `test_scan_bras.py`
2. Vérifier que le robot est debout
3. Vérifier les batteries
4. Consulter les logs d'erreur

---

**Dernière mise à jour** : 2025-10-06  
**Version du script** : nao_menu_simple.py
