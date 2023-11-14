from flask import Flask, render_template, request, jsonify
import openai
import requests  # To make HTTP requests to the photo-gen API

app = Flask(__name__)
openai.api_key = "YOUR_OPENAI_KEY"

@app.route('/')
def index():
    return render_template('index.html')

def format_recipe(recipe_text):
    response3 = openai.ChatCompletion.create(
        model="gpt-4",  # replace with chatgpt if you have a specific model name
        temperature = 0,
        messages=[{"role": "system", "content": f"Format the following recipe into HTML:\n\n{recipe_text}, the biggest head tag should be h2, do not contain ```html in the beginning"}],
    )
    recipe_html = response3.get("choices")[0]["message"]["content"]

    return recipe_html

def get_total_calories_from_recipe(recipe_text):
    # Construct a prompt to ask the API to calculate the total calories for the recipe.
    calorie_prompt = f"Calculate the total calories for the following recipe:\n\n{recipe_text}, don't show the calory of each part, JUST give the NUMBER of the total calories.(The format should be: Total calories: #the number#)"

    # Send the prompt to the OpenAI API.
    calorie_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": calorie_prompt}]
    )

    # Extract the calorie information from the response.
    # This will depend on the format of the response; we expect a simple number or a sentence from which we can extract the number.
    calories_text = calorie_response.get("choices")[0]["message"]["content"]
    # Extract just the number of calories from the response, assuming it starts with the number.
    #print(calories_text)

    return calories_text



@app.route('/remix', methods=['POST'])
def remix_recipe():
    ingredients = request.form['ingredients']
    diet = request.form['diet']
    requirement = request.form['requirement']

    # Call to OpenAI for alternative recipe suggestions
    response1 = openai.ChatCompletion.create(
        model="gpt-4",  # replace with chatgpt if you have a specific model name
        messages=[{"role": "system", "content": f"Imagine you are a famous cook, now someone wants you to recommend a recipe based on these {ingredients}, and he has a diet:{diet}(if it's blank, ignore it), and there are also some special requirements:{requirement}. Now can you generate a recipe based on these conditions? Note that you can only use the given ingredients, including seasonings. Also, you should generate the recipe text into a good format to help user understand the steps. Just give the recipe only."}],
    )
    recipe = response1.get("choices")[0]["message"]["content"]
    


    # Call to OpenAI for ingredient substitutions
    response2 = openai.ChatCompletion.create(
        model="gpt-4",  # replace with chatgpt if you have a specific model name
        messages=[{"role": "system", "content": f"Give a title, and a summary of the recipe(no more than 100 words): {recipe}. Remember to split the title and summary into 2 graphs"}],
    )
    recipe_desc = response2.get("choices")[0]["message"]["content"]
    recipe = format_recipe(recipe)
    #print(recipe)

    # Call to the photo-generation AI
    photo_response = openai.Image.create(
        model = "dall-e-3",
        prompt= recipe_desc + " The style is realistic.",
        n=1,
        size="1024x1024"
    )
    image_url = photo_response['data'][0]['url']
    #print(recipe)

    # Get the total calories for the recipe using the OpenAI API.
    calories = get_total_calories_from_recipe(recipe)


    return jsonify({
        'recipe': recipe,
        'recipe_desc': recipe_desc,
        'photo_url': image_url,
        'calories': calories
    })

if __name__ == '__main__':
    app.run(debug=True)
