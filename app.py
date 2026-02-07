import os
import asyncio
import aiohttp
import random
from flask import Flask, request, jsonify, render_template
from json_repair import repair_json
from flask_cors import CORS
import requests

app = Flask(__name__)
# Replace with your actual IFrame host URL once deployed
CORS(app) 

RCAC_API_KEY = os.environ.get('RCAC_API_KEY')
RCAC_URL = "https://genai.rcac.purdue.edu/api/chat/completions"

PROMPT = """<system_prompt>
You are an expert Physics Education Researcher and Cognitive Scientist. Your goal is to analyze student essays describing their strategy for solving a problem. You must determine if the student's proposed strategy will lead to the Correct Answer or a specific type of Misconception.
</system_prompt>
<user_prompt>
### TASK DESCRIPTION
I will provide you with a physics problem statement and a "Strategy Essay" written by a student.
1. Analyze the student's essay. Look for specific keywords or logical steps.
2. Identify if they are applying correct principles/concepts or falling into misconceptions.
3. Output your final reasoning and label as strictly valid JSON.
### Label Categories & Definitions
- 'correct': The reasoning and final answer are physically sound.
- 'direction': The student makes an error where their answer is in the exact opposite direction of the correct vector OR The student does not specifically state the direction they want to apply.
- 'position': The error arises from calculating forces or properties on a different object than the one asked OR The student does not specifically state the particular object they want to calculate for.
- 'position-direction': Both a 'position' error and a 'direction' error occur simultaneously in the student's response OR The student does not specifically state the direction nor the object they want to consider.
### Few-Shot Examples
**Example Student Essay1:**
The horizontal component of the force that the top block exerts on the bottom block includes friction acting between the blocks. There since the bottom block is moving with the bottom block the friction force must be less than the force applied and it must be acting in the opposite way as friction acts in the opposite direction of motion. To find the horizontal component the normal and gravitational force are assumed to be equal. So you have to calculate the friction force between the two blocks.
**Response:**{
    "classification": "position",
    "feedback": "You were right about friction (that it is the force that the top block exerts on the bottom block). And you even identified its direction (being the opposite of the applied force) correctly. But the question that's left is how to find its magnitude (absolute value)?"
}

**Example Student Essay2:**
To find the horizontal component of the force that the top block exerts on the bottom block, I would first set my system as the block on top and the surroundings as the block on the bottom and the force applied. Knowing that force is equal to mass times accleration, I can set the force on the block above by the block below equal to mass of my system times the acceleration of my system. Therefore, I can se force equal to the mass of the block on top times the force applied divided by the combined masses of both blocks. 
**Response:**{
    "classification": "direction",
    "feedback": "You described how to find the absolute value of the force correctly. But how would you determine its direction?"
}

**Example Student Essay3:**
As the acceleration of the blocks are the same, we can find the acceleration of both blocks in terms of the horizontal force and the acceleration of the top block in terms of friction. Then, by combining the two equations, we can find friction in terms of the mass of the blocks and the horizontal force. As friction is the only force exerted by the top block to the bottom block, then the horizontal compoenent of force that the top block exerts on the bottom block can be found.
**Response:**{
    "classification": "direction",
    "feedback": "You were right about the friction force being the force that the top block exerts on the bottom block. And you even found its magnitude correctly. However, you might have overlooked its direction, which is opposite to motion (in the -x direction). Drawing a free-body diagram for each block might have helped."
}

**Example Student Essay4:**
First you need to set up an equation for the force of the two blocks in a system together. Then you need to set up another equation for the force of friction between the top block and bottom block by making the top block the system and the bottom block the surroundings. Since the blocks are moving together, their acceleration is the exact same so you can set the two equations equal to each other to find the force of friction that the top block has on the bottom block.
**Response:**{
    "classification": "position-direction",
    "feedback": "If you consider the top block as the system and find the friction force that is applied to it by the bottom block, it will be the same in magnitude as the friction force applied to the bottom block by the top block, but with the opposite direction. Also, be careful with the masses of the blocks. It is easy to confuse m1 and m2 when calculating the answer."
}

**Example Student Essay5:**
To find the horizontal component of the force that top block exerts on the bottom block, I would first draw a diagram of the setup and then draw separate freebody diagrams of both blocks and also mark all the forces on each block. Then I would start writing the equation of Newton's Second law of motion to describe the net force acting in the horizontal direction. I would then do the same for the vertical direction and substitute into the first equation. I would also solve for each of the forces and then solve the equation to get my answer.
**Response:**{
    "classification": "position",
    "feedback": "Drawing a free-body diagram for each block separately was a good idea. This will help you identify the direction of the force to be found correctly. However, be careful with the actual equations (based on Newton Second Law) that you write. Since each block has its own unique mass, each equation will have terms corresponding to that mass. And if you need to perform some algebraic calculations, track which masses cancel out if any."
}

**Example Student Essay6:**
I would first go about this by finding the total mass of the system. Then given the total mass of the system, I know the force and mass, and using Newton's Second Law, I can find the acceleration of the system. After finding the acceleration I can multiply it by the top block, which will then give me the horizontal component of the force that top block exerts on the bottom block. Then I have to note that it is in the left direction, so the final answer would be a negative force value. 
**Response:**{
    "classification": "correct",
    "feedback": "Solid logic. Just double check your calculations at the end."
}

**Example Student Essay7:**
To find the horizontal component of the force that the top block exerts on the bottom block, you must first find the total acceleration of the system of both blocks by divings the known horizontal force by the combined mass of both blocks. Then multiply this acceleration with the mass of the top block and then make this number negative since its force is acting opposite the motion of the blocks. This is the horizontal component of the force that the top block exerts on the bottom block.
**Response:**{
    "classification": "correct",
    "feedback": "Great strategy! Now you only need to calculate the result."
}

**Example Student Essay8:**
To find the force that the top block exerts on the bottom block, there must be two clear systems defined: one, that considers both blocks, and one that considers the bottom block.   Since the force is applied to the bottom block only, the top block does not have any force except that of friction which goes in the direction of the motion of the system of blocks.    The second system considers only the force of the bottom block.   The result is the fraction of the initial force on the bottom block, which are proportional to their masses.
**Response:**{
    "classification": "position-direction",
    "feedback": "You were right on spot about considering two systems to solve this problem: one with both blocks as system, another as the bottom block only. And indeed, when you consider the bottom block and the forces that act on it, the force from the top block which we need to find is proportional to the external force applied. But the key is to determine which mass exactly it is proportional to. The top or the bottom one? Also, don't forget about the direction of that force."
}

**Example Student Essay9:**
I would find the  the net force of the system when it is both blocks, and solve for acceleration. Then I would find the net force of the system when it is only the top block, using the acceleration found before I would replace it in this new net force equation. So this equation should consist of the blocks mass on top multiplied by the force applied then divided by the sum of the two blocks. This will then solve for the horizontal component of the force that the top block exerts onthe bottom block.
**Response:**{
    "classification": "position-direction",
    "feedback": "You are right on spot! But be careful with the masses here, it is easy to swap their values in calculations. Also, what can you say about the direction of the force that you found?"
}

**Example Student Essay10:**
The strategy that I would use to find the horizontal component of the force the top block exerts on the bottom block is I would first define my ssytem as both blocks. Then I would redefine my system as just bottom block because a force acting on that block is what we are trying to solve for. Then I would substitute the acceleration in the second system using the first system because all of the blocks and system are accelerating at the same rate. Then I would be able to solve for the force on the bottom blok by the top block.
**Response:**{
    "classification": "position",
    "feedback": "What you described will yield only the net force on the bottom block. But the question asked for the force exerted on the bottom block by the top block specifically. This force is a part of the force you found but there is another part, which the applied force."
}

**Example Student Essay11:**
First I would determine the net forces when the two blocks are part of the system and the surroundings are just the earth. Then I would repeat the process with only block m2 being the system and m1 and the earth being the surroundings. I am aware that they move together which means acceleration is the same for both blocks. Then solving the first equation for acceleration and plugging it in the second would help me determine the force m2 exerts on m1.
**Response:**{
    "classification": "direction",
    "feedback": "Since you selected the bottom block m2 as the system, you found the force that the block m1 exerts on it. However, the question asked for the force that m2 exerts on m1, which is the same in magnitude but opposite in direction."
}

**Example Student Essay12:**
You would first find the net horizontal force of the first block on top of the other one. Then you find the free body diagram of horizontal forces acting on the second block below the top one. You then equate the reaction force of the friction, the applied force, then substitute the force of friction for the one found for the first block because they are equal. Then you solve for Force of friction because this is the only horizontal component the top block exerts on the bottom block. 
**Response:**{
    "classification": "correct",
    "feedback": "Excellent strategy!"
}

### TEST CASE
<quiz_problem>
A block of known mass rests on top of another block of known mass, which in turn rests on a frictionless horizontal surface. When a known horizontal force is applied to the bottom block the two blocks move together.
Describe in WORDS the strategy you would use to find the horizontal component of the force that top block exerts on the bottom block.
</quiz_problem>
<essay>
{STUDENT_STRATEGY_ESSAY}
</essay>
### INSTRUCTIONS
Analyze the "Student Essay" above and provide the JSON output.
### OUTPUT FORMAT
{{
"classification": Choose one from ['correct', 'direction', 'position', 'position-direction'],
"confidence": How confident the classification is (scale of 1 to 5, 5 being most confident),
"secondary_classification": What would be the second most likely label?
"feedback": Feedback message (in 50 words) to students based on their essay. If their essay is classified to make a certain type of mistake, the feedback should highlight that aspect. If it is classified as correct, the feedback can be general and notify some common mistakes that can be made.
}}
### Constraint
- Output ONLY the json.
- Do NOT provide reasoning, explanations, or introductory text.
"""

MAX_RETRIES = 5
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=240)

async def get_single_completion(prompt, model_ckpt="deepseek-r1:70b"):
    url = "https://genai.rcac.purdue.edu/api/chat/completions"
    headers = {
        "Authorization": f"Bearer {RCAC_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model_ckpt,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False 
    }

    async with aiohttp.ClientSession() as session:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(url, headers=headers, json=body, timeout=REQUEST_TIMEOUT) as response:
                    # Success case
                    if response.status == 200:
                        data = await response.json()
                        data_str = data['choices'][0]['message']['content']
                        data_obj = json.loads(repair_json(data_str))
                        assert "feedback" in data_obj
                        return data_obj # Returns just the string
                    
                    # Retryable server errors (429 = Rate Limit, 5xx = Server issues)
                    if response.status in [429, 500, 502, 503, 504]:
                        error_msg = f"Status {response.status}"
                        # Fall through to the retry logic below
                    else:
                        # Non-retryable errors (e.g., 401 Unauthorized, 404 Not Found)
                        error_text = await response.text()
                        return f"Client Error: {response.status} - {error_text}"

            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                error_msg = str(e)

            # Retry Logic: Exponential Backoff with Jitter
            if attempt < MAX_RETRIES - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Attempt {attempt + 1} failed ({error_msg}). Retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
            else:
                return f"Failed after {MAX_RETRIES} attempts. Last error: {error_msg}"

@app.route('/')
def index():
    # This looks inside the /templates folder
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
async def chat():
    data = request.json
    student_email = data.get('student_email', 'Unknown')
    essay_content = data.get('message')

    # RESEARCH LOGGING: Captured by Render Logs
    print(f"--- RESEARCH LOG ENTRY ---")
    print(f"STUDENT: {student_email}")
    print(f"ESSAY: {essay_content}")
    print(f"--------------------------")

    headers = {
        "Authorization": f"Bearer {RCAC_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        # "model": "llama4:latest",
        "model": "deepseek-r1:70b",
        "messages": [{"role": "user", "content": essay_content}]
    }

    try:
        output = await get_single_completion(PROMPT.format(STUDENT_STRATEGY_ESSAY=essay_content))
        
        print(f"AI_RESPONSE: {output}")
        print(f"--------------------------")
        return jsonify({"reply": output["feedback"]})
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"--------------------------")
        return jsonify({"reply": "The Quiz Assistant is currently unavailable. Please try again later."}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))