import os
import logging
import requests
from dotenv import load_dotenv

# ეს ხაზი კითხულობს .env ფაილს და ტვირთავს სისტემურ ცვლადებში
load_dotenv()
# ვქმნით ლოგერს ამ მოდულისთვის
logger = logging.getLogger(__name__)

def get_recipe_nutrition(title):
    api_key = os.environ.get('SPOONACULAR_API_KEY')  
  
    url = "https://api.spoonacular.com/recipes/guessNutrition"
    

    params = {
        'apiKey': api_key,
        'title': title,         
        'servings': 1,
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # თუ სიაა, ვაერთიანებთ ახალ ხაზებზე, თუ უკვე სტრიქონია - ვტოვებთ
   
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # ვკრებთ ინგრედიენტების ჯამურ θეროებს (ან ვიყენებთ ნუტრიენტების ანალიზის ენდპოინტს)
            #calories, protein, carbs, fat = 0, 0, 0, 0
            calories = data.get("calories", {}).get("value", 0)
            protein = data.get("protein", {}).get("value", 0)
            carbs = data.get("carbs", {}).get("value", 0)
            fat = data.get("fat", {}).get("value", 0)   
           # 1. წარმატებული API პასუხის ლოგირება (Info დონე)
            logger.info(f"Successfully fetched nutrition for '{title}': Calories={calories}, Protein={protein}, Carbs={carbs}, Fat={fat}")
            
            return {
                "calories": round(calories),
                "protein": round(protein, 1),
                "carbs": round(carbs, 1),
                "fat": round(fat, 1),
                "data_source": data
            }
        else:
            # 2. API Request Error (თუ სტატუს კოდი 200 არ არის - მაგ: ლიმიტი ამოიწურა ან ქიმი არასწორია)
            logger.error(f"Spoonacular API Error: Status {response.status_code} for recipe '{title}'. Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # 3. ქსელური შეცდომა ან ტაიმაუტი (API Request Error)
        logger.error(f"API Request Exception while fetching nutrition for '{title}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching nutrition for '{title}': {str(e)}")
        return None

