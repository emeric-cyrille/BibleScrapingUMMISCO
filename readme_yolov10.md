
## **YOLOv10 - Détection d'objets en temps réel**  

Ce dépôt contient tout le nécessaire pour **installer, entraîner et exécuter YOLOv10**, un modèle avancé de détection d'objets en une seule étape. YOLOv10 est optimisé pour une inférence rapide et précise, idéal pour des applications en **vision par ordinateur**.

📌 **Lien vers le dépôt GitHub** : [https://github.com/THU-MIG/yolov10]  

---

## **🛠 Installation**  

Il est recommandé d'utiliser un **environnement Conda** pour une gestion optimale des dépendances.  

```bash
# Créer un environnement virtuel Conda
conda create -n yolov10 python=3.9
conda activate yolov10

# Installer les dépendances
pip install -r requirements.txt
pip install -e .
```

**🔹 Remarque :**  
- Il est préférable d’utiliser **Pycharm** pour ce projet, car il offre un bon support pour les environnements Conda et facilite le développement.  
- Assurez-vous d'avoir une **carte GPU compatible avec CUDA** pour de meilleures performances.  

---

## **🚀 Démo - Tester le modèle**  

Vous pouvez exécuter une **interface web** pour tester la détection d’objets avec YOLOv10 :  

```bash
python app.py
```

Puis ouvrez votre navigateur et accédez à **http://127.0.0.1:7860**.  

---


## **🎯 Entraînement du modèle**  

Lancez l'entraînement sur COCO avec **500 epochs** et un batch de **256** images :  

```bash
yolo detect train data=coco.yaml model=yolov10n/s/m/b/l/x.yaml epochs=500 batch=256 imgsz=640 device=0,1,2,3,4,5,6,7
```

Ou en Python :  

```python
from ultralytics import YOLOv10

model = YOLOv10()
# Pour fine-tuner un modèle pré-entraîné
# model = YOLOv10.from_pretrained('jameslahm/yolov10{n/s/m/b/l/x}')
model.train(data='coco.yaml', epochs=500, batch=256, imgsz=640)
```

---

## **📤 Push du modèle fine-tuné sur Hugging Face**  

Après entraînement, vous pouvez **envoyer votre modèle sur Hugging Face Hub** :  

```python
model.push_to_hub("<your-hf-username-or-organization/yolov10-finetuned-crop-detection")
# Pour un modèle privé :
model.push_to_hub("<your-hf-username-or-organization/yolov10-finetuned-crop-detection", private=True)
```

---

## **🔍 Prédiction avec YOLOv10**  

```bash
yolo predict model=jameslahm/yolov10{n/s/m/b/l/x}
```

Ou en Python :  

```python
from ultralytics import YOLOv10

model = YOLOv10.from_pretrained('jameslahm/yolov10{n/s/m/b/l/x}')
model.predict()
```

---

Ce README est **clair, structuré et détaillé** pour faciliter la prise en main du projet **YOLOv10**. 🚀  
