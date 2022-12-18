from django.http import JsonResponse

import numpy as np
import pandas as pd
import random

from . import models

import  os

from rest_framework.views import APIView
from django.http import  JsonResponse
import json

POEM_ORDER = ["EA","NO","CE","NA","CO","NE","CA","EO","NC","AO"]

INITIAL_PERSONALITY_VALUES = {"C":0,"E":0,"O":0,"N":0,"A":0}
MID = 0
HALF_DEVIATION = 0.5

# Create your views here.

curr_file = os.path.split(__file__)
questions_df = pd.read_csv(os.path.join(curr_file[0],"big_five_questions.csv"))
poetry_df = pd.read_csv(os.path.join(curr_file[0],"poetry_lines.csv"))

class GetQuestions(APIView):
    def get(self,request):
        arr = np.array(questions_df.index)
        question_choices = questions_df[questions_df.index.isin(arr)]
        response = []
        for index, row in question_choices.iterrows():
            response.append({x:row[x] for x in ["question","E","C","O","N","A"]})
        random.shuffle(response)
        return JsonResponse({"questions":response})

class GetResults(APIView):
    def post(self, request):
        name = json.loads(request.body)["name"]
        answers = json.loads(request.body)["answers"]
        personality_values = INITIAL_PERSONALITY_VALUES.copy()

        for answer in answers:
            for trait in "ECONA":
                personality_values[trait] +=(float(answer["value"])-3)*answer[trait]

        #divide by the sum of all correlation, this gives us a generic 1-5 score, then -1 fives us 0 to 4
        for trait in "ECONA":
            positive_corr = questions_df[questions_df[trait]>0][trait].sum()
            negative_corr = questions_df[questions_df[trait]<0][trait].sum()
            personality_values[trait] /= (positive_corr+abs(negative_corr))

        personnality_degrees = {x: degree(personality_values[x]) for x in personality_values}

        poem = []
        for diad in POEM_ORDER:

            trait1,trait2 = diad[0],diad[1]
            degree1, degree2 = personnality_degrees[trait1], personnality_degrees[trait2]

            poem.append((poetry_df[(poetry_df['Trait1'] == trait1) & (poetry_df["Trait2"] == trait2) & (poetry_df["Degree1"] == degree1) & (
                    poetry_df["Degree2"] == degree2)])["Line1"].iloc[0])
            poem.append((poetry_df[(poetry_df['Trait1'] == trait1) & (poetry_df["Trait2"] == trait2) & (
                        poetry_df["Degree1"] == degree1) & (
                                           poetry_df["Degree2"] == degree2)])["Line2"].iloc[0])

        for line in [
            "Roses red, violets are blue",
            "Sweet words of art do not harm",
            "And I am {}, the poem".format(name),
            "That's a reflection of you!"]:
            poem.append(line)

        c_sharpness = personality_values["C"]*25+50
        a_sharpness = 50 - personality_values["A"] * 25
        n_sharpness = 50 - personality_values["N"] * 25

        sharpness = (c_sharpness+a_sharpness+n_sharpness)/3

        record = models.UserRecord()
        record.E = personality_values["E"]
        record.A = personality_values["A"]
        record.C = personality_values["C"]
        record.N = personality_values["N"]
        record.O = personality_values["O"]
        record.name = name
        record.save()

        return JsonResponse({"poem": poem, "sharpness":round(sharpness,0)})

def degree(value):
    return "Low" if value<(MID-HALF_DEVIATION) else ("High" if value>(MID+HALF_DEVIATION) else "Mid")


