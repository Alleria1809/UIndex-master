import ast

from main import app
from flask import render_template, redirect, url_for, flash, get_flashed_messages, request, jsonify,send_from_directory
from main.forms import UniversityForm, emailForm
import pyrebase
import csv
import os

from wordcloud import WordCloud, STOPWORDS
from flask_mail import Mail, Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import smtplib
import email.mime.text
import email.mime.multipart


firebaseConfig = {
    "apiKey": "AIzaSyCtMDzX72ZtbennGItRiQtyUzcH0owFgOk",
    "authDomain": "dsci551-114514.firebaseapp.com",
    "databaseURL": "https://dsci551-114514-default-rtdb.firebaseio.com",
    "projectId": "dsci551-114514",
    "storageBucket": "dsci551-114514.appspot.com",
    "messagingSenderId": "183909952397",
    "appId": "1:183909952397:web:218c68faea75b9692debc4"
}

stopwords = set(STOPWORDS)
stopwords.add('student')
stopwords.add('students')
stopwords.add('make')
stopwords.add('campus')
stopwords.add('university')
stopwords.add('want')

# email address settings
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER="smtp.gmail.com",
    # MAIL_PORT=587,
    # MAIL_USE_TLS=True,
    MAIL_PORT=465,  # 163--465
    MAIL_USE_SSL=True,
    MAIL_USE_TLS=False,
    MAIL_USERNAME="xiaoyigu1809@gmail.com",   # my email address
    MAIL_PASSWORD="2022dsci551",          # my email password
    MAIL_DEFAULT_SENDER=("xiaoyigu1809@gmail.com"),  # defult sending address
    MAIL_DEBUG=True,
))

# create a mail application
mail = Mail(app)   

def create_wc(text):
    if not text:
        text += 'Comment None!'
    cloud = WordCloud(background_color=(215,211,198), max_words=300, collocations=False, width=800, height=500, stopwords=stopwords).generate(text)
    cloud.to_file("./main/static/WordCloud.png")
    return 1


def list_to_text(l):
    return " ".join(l)


def fToC(f):
    if f == '':
        return ''
    return round((float(f) - 32) * 5 / 9, 1)


def avg(list):
    if len(list) == 0:
        return 0
    return sum(list) / len(list)


def inchTomm(i):
    if i == '':
        return ''
    return round(float(i) * 25.4, 1)


def tempToHex(temp):
    temp = float(temp)
    if temp <= 0.3:
        return '#2e6f95B3'
    elif temp <= 9.5:
        return '#2a6f97B3'
    elif temp <= 14.4:
        return '#2c7da0B3'
    elif temp <= 19.3:
        return '#468fafB3'
    elif temp <= 24.4:
        return '#61a5c2B3'
    elif temp <= 28:
        return '#98c1d9B3'
    elif temp <= 32:
        return '#a9d6e5B3'
    elif temp <= 34:
        return '#e0fbfcB3'
    elif temp <= 38.4:
        return '#f4f3eeB3'
    elif temp <= 42:
        return '#ffefd3B3'
    elif temp <= 44.8:
        return '#ffc49bB3'
    elif temp <= 48.7:
        return '#ffc971B3'
    elif temp <= 51.2:
        return '#ffb627B3'
    elif temp <= 53.6:
        return '#ff9505B3'
    elif temp <= 57.6:
        return '#ffba08B3'
    elif temp <= 61:
        return '#faa307B3'
    elif temp <= 64:
        return '#f48c06B3'
    elif temp <= 70.4:
        return '#e85d04B3'
    elif temp <= 76.8:
        return '#dc2f02B3'
    elif temp <= 83.2:
        return '#d00000B3'
    else:
        return '#ae2012B3'


def pcpToHex(pcp):
    pcp = float(pcp)
    if pcp < 0.54:
        return '#b6ad90B3'
    elif pcp <= 1.04:
        return '#f2e8cfB3'
    elif pcp <= 1.54:
        return '#e9f5dbB3'
    elif pcp <= 2.04:
        return '#d8f3dcB3'
    elif pcp <= 2.54:
        return '#b7e4c7B3'
    elif pcp <= 3.04:
        return '#95d5b2B3'
    elif pcp <= 3.54:
        return '#74c69dB3'
    elif pcp <= 4.04:
        return '#99e2b4B3'
    elif pcp <= 4.54:
        return '#88d4abB3'
    elif pcp <= 5.04:
        return '#78c6a3B3'
    elif pcp <= 5.54:
        return '#67b99aB3'
    elif pcp <= 8.04:
        return '#56ab91B3'
    elif pcp <= 12.04:
        return '#469d89B3'
    else:
        return '#358f80B3'


def pcpToColor(pcp):
    pcp = float(pcp)
    if pcp <= 5.54:
        return 'black'
    else:
        return 'white'


def levelToHex(level):
    if level == '':
        return
    elif level == 'Very Low':
        return '#d4e09bB8'
    elif level == 'Low':
        return '#cbdfbdB8'
    elif level == 'Moderate':
        return '#f6f4d2B8'
    elif level == 'High':
        return '#f19c79B8'
    elif level == 'Very High':
        return '#a44a3fB8'


def walkingLevelToHex(level):
    if level == '':
        return
    elif level == 'Very Low':
        return '#a44a3fB8'
    elif level == 'Low':
        return '#f19c79B8'
    elif level == 'Moderate':
        return '#f6f4d2B8'
    elif level == 'High':
        return '#cbdfbdB8'
    elif level == 'Very High':
        return '#d4e09bB8'

def pcpScore(value):
    avg = 30.21
    result = abs(value - avg)
    if result <= 5:
        return 30
    elif result <= 10:
        return 27
    elif result <= 15:
        return 24
    elif result <= 20:
        return 21
    elif result <= 25:
        return 18
    elif result <= 30:
        return 16
    elif result <= 40:
        return 15
    else:
        return 14


def tempScore(l):
    result = 0
    for i in l:
        result += abs(68 - i)
    if result <= 10:
        return 60
    elif result <= 30:
        return 58
    elif result <= 50:
        return 55
    elif result <= 76:
        return 53
    elif result <= 105:
        return 50
    elif result <= 143:
        return 46
    elif result <= 172:
        return 43
    elif result <= 201:
        return 40
    elif result <= 241:
        return 35
    elif result <= 279:
        return 30
    elif result <= 305:
        return 28
    else:
        return 24


def tuitionScore(tuition):
    if tuition <= 15896:
        return 25
    elif tuition <= 25560:
        return 23
    elif tuition <= 35100:
        return 21
    elif tuition <= 44800:
        return 19
    else:
        return 18


def alumniScore(a):
    if a >= 40000:
        return 25
    elif a >= 25222:
        return 24
    elif a >= 18400:
        return 23
    elif a >= 12000:
        return 22
    else:
        return 21


def rankScore(r):
    r = int(r)
    if r <= 8:
        return 50
    elif r <= 16:
        return 43
    elif r <= 30:
        return 39
    elif r <= 50:
        return 35
    elif r <= 70:
        return 31
    elif r <= 100:
        return 27
    elif r <= 160:
        return 24
    elif r <= 200:
        return 21
    elif r <= 250:
        return 18
    else:
        return 15


def trafficScore(dict):
    score = 0
    walking = float(dict['Walking_Main_Means'][:-1])
    car = float(dict['Car_Main_Means'][:-1])
    bike = float(dict['Bike_Main_Means'][:-1])
    train = float(dict['Train_Metro_Main_Means'][:-1])
    index = float(dict['Traffic_Index'])
    time = float(dict['Time_Index_in_minutes'])
    co2 = float("".join(dict['CO2_Emission_Index'].split(',')))
    m = max([walking, car, bike, train])
    if walking == m:
        score += 40
    elif car == m:
        score += 10
    elif bike == m:
        score += 35
    elif train == m:
        score += 25

    if index <= 70:
        score += 20
    elif index <= 130:
        score += 15
    elif index <= 188:
        score += 12
    elif index <= 220:
        score += 10
    else:
        score += 7

    if time <= 13.5:
        score += 20
    elif time <= 26:
        score += 17
    elif time <= 32:
        score += 14
    elif time <= 41:
        score += 11
    else:
        score += 8

    if co2 <= 1000:
        score += 20
    elif co2 <= 3200:
        score += 18
    elif co2 <= 5600:
        score += 16
    elif co2 <= 7200:
        score += 14
    elif co2 <= 9000:
        score += 10
    elif co2 <= 12500:
        score += 6
    else:
        score += 4

    return score


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home_page():
    form = UniversityForm()
    if request.method == "POST" and form.validate_on_submit():
        if form.validate_on_submit():
            firebase = pyrebase.initialize_app(firebaseConfig)
            fdb = firebase.database()
            # order can be followed by:  equal_to, start_at() larger than,
            ref = fdb.child("rankings").order_by_child("name").equal_to(
                str.upper(form.universityName.data)).limit_to_first(1).get()
            if ref.each() is None:
                flash('University not found! Please type again.', category='danger')
            else:
                name = form.universityName.data
                r = None
                for rr in ref.each():
                    if rr.val() is not None:
                        r = rr.val()
                if r is None:
                    render_template('home.html', form=form)
                else:
                    climate_ref = fdb.child('university_climate').order_by_child("university").equal_to(
                        form.universityName.data).limit_to_first(1).get().each()
                    if len(climate_ref) == 1:
                        climate_dict = climate_ref[0].val()
                    else:
                        climate_dict = climate_ref[1].val() if climate_ref[0].val() is None else climate_ref[0].val()

                    crime_ref = fdb.child('university_crime').order_by_child("university").equal_to(
                        form.universityName.data).limit_to_first(1).get().each()
                    if len(crime_ref) == 1:
                        crime_dict = crime_ref[0].val()
                    else:
                        crime_dict = crime_ref[1].val() if crime_ref[0].val() is None else climate_ref[1].val()

                    traffic_ref = fdb.child('university_traffic').order_by_child("University").equal_to(
                        form.universityName.data).limit_to_first(1).get().each()
                    if len(traffic_ref) == 1:
                        traffic_dict = traffic_ref[0].val()
                    else:
                        traffic_dict = traffic_ref[1].val() if traffic_ref[0].val() is None else traffic_ref[1].val()

                    desc_ref = fdb.child('university_description').order_by_child("university").equal_to(
                        form.universityName.data).limit_to_first(1).get().each()
                    if len(desc_ref) == 1:
                        desc_dict = desc_ref[0].val()
                    else:
                        desc_dict = desc_ref[1].val() if desc_ref[0].val is None else desc_ref[1].val()

                    res = fdb.child('university_crime').get().each()
                    loc_list, ci_list, whb_list, wbm_list, wcs_list, wtc_list, wa_list, wbsc_list, wbi_list, dg_list, pc_list, pv_list, pcb_list, sd_list, sn_list = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
                    for re in res:
                        if 'loc' in re.val():
                            loc_list.append(re.val()['loc'])
                        if 'ci' in re.val():
                            ci_list.append(re.val()['ci'])
                        if 'whb' in re.val():
                            whb_list.append(re.val()['whb'])
                        if 'wcs' in re.val():
                            wcs_list.append(re.val()['wcs'])
                        if 'wbm' in re.val():
                            wbm_list.append(re.val()['wbm'])
                        if 'wtc' in re.val():
                            wtc_list.append(re.val()['wtc'])
                        if 'wa' in re.val():
                            wa_list.append(re.val()['wa'])
                        if 'wbi' in re.val():
                            wbi_list.append(re.val()['wbi'])
                        if 'wbsc' in re.val():
                            wbsc_list.append(re.val()['wbsc'])
                        if 'dg' in re.val():
                            dg_list.append(re.val()['dg'])
                        if 'pc' in re.val():
                            pc_list.append(re.val()['pc'])
                        if 'pv' in re.val():
                            pv_list.append(re.val()['pv'])
                        if 'pcb' in re.val():
                            pcb_list.append(re.val()['pcb'])
                        if 'sd' in re.val():
                            sd_list.append(re.val()['sd'])
                        if 'sn' in re.val():
                            sn_list.append(re.val()['sn'])

                    avg_list = [avg(loc_list), avg(ci_list),avg(whb_list), avg(wbm_list), avg(wcs_list),avg(wtc_list),avg(wa_list),avg(wbsc_list),avg(wbi_list),
                                avg(dg_list),avg(pc_list),avg(pv_list),avg(pcb_list),avg(sd_list),avg(sn_list)]

                    tempMax_data = [
                        ("Jan", (climate_dict['tmax_in_Jan'])),
                        ("Feb", (climate_dict['tmax_in_Feb'])),
                        ("Mar", (climate_dict['tmax_in_Mar'])),
                        ("Apr", (climate_dict['tmax_in_Apr'])),
                        ("May", (climate_dict['tmax_in_May'])),
                        ("Jun", (climate_dict['tmax_in_June'])),
                        ("Jul", (climate_dict['tmax_in_July'])),
                        ("Aug", (climate_dict['tmax_in_Aug'])),
                        ("Sep", (climate_dict['tmax_in_Sep'])),
                        ("Oct", (climate_dict['tmax_in_Oct'])),
                        ("Nov", (climate_dict['tmax_in_Nov'])),
                        ("Dec", (climate_dict['tmax_in_Dec']))
                    ]

                    tempMin_data = [
                        ("Jan", (climate_dict['tmin_in_Jan'])),
                        ("Feb", (climate_dict['tmin_in_Feb'])),
                        ("Mar", (climate_dict['tmin_in_Mar'])),
                        ("Apr", (climate_dict['tmin_in_Apr'])),
                        ("May", (climate_dict['tmin_in_May'])),
                        ("Jun", (climate_dict['tmin_in_June'])),
                        ("Jul", (climate_dict['tmin_in_July'])),
                        ("Aug", (climate_dict['tmin_in_Aug'])),
                        ("Sep", (climate_dict['tmin_in_Sep'])),
                        ("Oct", (climate_dict['tmin_in_Oct'])),
                        ("Nov", (climate_dict['tmin_in_Nov'])),
                        ("Dec", (climate_dict['tmin_in_Dec']))
                    ]

                    pcp_data = [
                        ("Jan", (climate_dict['pcp_in_Jan'])),
                        ("Feb", (climate_dict['pcp_in_Feb'])),
                        ("Mar", (climate_dict['pcp_in_Mar'])),
                        ("Apr", (climate_dict['pcp_in_Apr'])),
                        ("May", (climate_dict['pcp_in_May'])),
                        ("Jun", (climate_dict['pcp_in_June'])),
                        ("Jul", (climate_dict['pcp_in_July'])),
                        ("Aug", (climate_dict['pcp_in_Aug'])),
                        ("Sep", (climate_dict['pcp_in_Sep'])),
                        ("Oct", (climate_dict['pcp_in_Oct'])),
                        ("Nov", (climate_dict['pcp_in_Nov'])),
                        ("Dec", (climate_dict['pcp_in_Dec']))
                    ]

                    trafficMeans_list = [
                        ("Bus", 'Bus_Trolleybus_Main_Means'),
                        ("Bike", 'Bike_Main_Means'),
                        ("Car", 'Car_Main_Means'),
                        ("Motorbike", 'Motorbike_Main_Means'),
                        ("Metro & Train", 'Train_Metro_Main_Means'),
                        ("Tram & Streetcar", 'Tram_Streetcar_Main_Means'),
                        ("Walking", 'Walking_Main_Means'),
                        ("WFH & SFH", 'Working_from_Home_Main_Means'),
                    ]

                    trafficDist_list = [
                        ("Walking", 'Distance_Walking'),
                        ("Car", 'Distance_Car'),
                        ("Bike", 'Distance_Bike'),
                        ('Motorbike', 'Distance_Motorbike'),
                        ('Bus', 'Distance_Bus_Trolleybus'),
                        ('Metro & Train', 'Distance_Train_Metro'),
                    ]

                    crime_list = [
                        ("Level of Overall Crime", 'loc', 'loc_level'),
                        ("Crime increasing in the past 3 years", 'ci', 'ci_level'),
                        ("Home Broken and Things Stolen", 'whb', 'whb_level'),
                        ("Being Mugged or Robbed", 'wbm', 'wbm_level'),
                        ("Car Stolen", 'wcs', 'wcs_level'),
                        ("Things from Car Stolen", 'wtc', 'wtc_level'),
                        ("Being Attacked", 'wa', 'wa_level'),
                        ("Being Attecked due to race/gender/religion", 'wbsc', 'wbsc_level'),
                        ("Being Insulted", 'wbi', 'wbi_level'),
                        ("People using or dealing drugs", 'dg', 'dg_level'),
                        ("Property Crime - Vandalism or Theft", 'pc', 'pc_level'),
                        ("Assault or Armed Robbery", 'pv', 'pv_level'),
                        ("Corruption and bribery", 'pcb', 'pcb_level'),

                    ]

                    walking_list = [
                        ("Safety Walking during Daylight", 'sd', 'sd_level'),
                        ("Safety Walking during Night", 'sn', 'sn_level'),
                    ]

                    trafficMeans_data = []
                    for label, key in trafficMeans_list:
                        if key in traffic_dict and float(traffic_dict[key][:-1]) != 0:
                            trafficMeans_data.append((label, traffic_dict[key]))

                    trafficDist_data = []
                    for label, key in trafficDist_list:
                        if key in traffic_dict:
                            trafficDist_data.append((label, traffic_dict[key]))

                    crime_data = []
                    for label, key1, key2 in crime_list:
                        if key1 in crime_dict:
                            crime_data.append((label, crime_dict[key1], crime_dict[key2]))

                    walking_data = []
                    for label, key1, key2 in walking_list:
                        if key1 in crime_dict:
                            walking_data.append((label, crime_dict[key1], crime_dict[key2]))

                    crimeType_data = []
                    if len(crime_dict) != 1:
                        crimeType_data = [
                            ("Overall Crime Index", crime_dict['loc']),
                            ("Danger of Walking", 100 - (float(crime_dict['sd']) + float(crime_dict['sn'])) / 2),
                            ("Crimes Against Persons",
                             (float(crime_dict['wbm']) + float(crime_dict['wa']) + float(crime_dict['pv'])) / 3),
                            ("Crimes Against Property", (float(crime_dict['whb']) + float(crime_dict['wcs']) + float(
                                crime_dict['wtc']) + float(crime_dict['pc'])) / 4),
                            ("Hate Crimes", (float(crime_dict['wbsc']) + float(crime_dict['wbi'])) / 2),
                            ("Crimes Against Morality", (float(crime_dict['dg']) + float(crime_dict['pcb'])) / 2)
                        ]

                    tempMax_labels = [row[0] for row in tempMax_data]
                    tempMax_values = [row[1] for row in tempMax_data]
                    tempMin_labels = [row[0] for row in tempMin_data]
                    tempMin_values = [row[1] for row in tempMin_data]
                    pcp_labels = [row[0] for row in pcp_data]
                    pcp_values = [float(row[1]) for row in pcp_data]
                    trafficMeans_labels = [row[0] for row in trafficMeans_data]
                    trafficMeans_values = [float(row[1][:-1]) for row in trafficMeans_data]
                    maxTrafficMeans = max(trafficMeans_values) if len(trafficMeans_values) != 0 else 0

                    trafficDist_labels = [row[0] for row in trafficDist_data]
                    trafficDist_values = [float(row[1]) for row in trafficDist_data]
                    crime_labels = [row[0] for row in crime_data]
                    crime_values = [float(row[1]) for row in crime_data]
                    crime_levels = [row[2] for row in crime_data]

                    crimeType_labels = [row[0] for row in crimeType_data]
                    crimeType_values = [float(row[1]) for row in crimeType_data]

                    walking_labels = [row[0] for row in walking_data]
                    walking_values = [float(row[1]) for row in walking_data]
                    walking_levels = [row[2] for row in walking_data]

                    avgTemp_values = [(float(i) + float(j)) / 2 for i, j in zip(tempMax_values, tempMin_values)]
                    # safety: avg of all scores except for walking scores and 1 - avg of walking scores
                    # climate: 60 for temperature and 40 for pcp. use 30.21 inches as an optimal annual pcp and 68F as optimal avg temp of min and max
                    # academic: 25 for tuition, 25 for alumni, and 50 for ranking.\
                    # convenience: 40 for means, 20 for time_index, 20 for traffic_index, 20 for co2 emission
                    general_list = [
                        ("Safety", (sum([100 - float(i) for i in crimeType_values]) / len(crimeType_values)) if len(
                            crimeType_values) != 0 else 0),
                        ("Climate", pcpScore(sum(pcp_values)) + tempScore(avgTemp_values)),
                        ("Academic",
                         tuitionScore(r['tuition_and_fees']) + alumniScore(r['undergraduate_enrollment']) + rankScore(
                             r['rank'])),
                        ("Convenience", 0 if len(trafficMeans_values) == 0 else trafficScore(traffic_dict))
                    ]


                    general_list.append(("Overall", 0.6 * general_list[2][1] + 0.15 * general_list[-1][1] + 0.15 * general_list[0][1] +  0.1 * general_list[1][1]))

                    general_labels = [row[0] for row in general_list]
                    general_values = [round(row[1]) for row in general_list]

                    txt = list_to_text(ast.literal_eval(r['corpus']))
                    create_wc(txt)
                    r['tuition_and_fees'] = int(r['tuition_and_fees'])

                    return render_template('info.html', university_dict=r, climate_dict=climate_dict,
                                           crime_dict=crime_dict,
                                           traffic_dict=traffic_dict, f=fToC, i=inchTomm, t=tempToHex,
                                           tempMax_labels=tempMax_labels,
                                           tempMax_values=tempMax_values, tempMin_labels=tempMin_labels,
                                           tempMin_values=tempMin_values,
                                           pcp_labels=pcp_labels, pcp_values=pcp_values,
                                           trafficMeans_labels=trafficMeans_labels,
                                           trafficMeans_values=trafficMeans_values,
                                           trafficDist_labels=trafficDist_labels,
                                           trafficDist_values=trafficDist_values, maxTrafficMeans=maxTrafficMeans,
                                           p=pcpToHex, pC=pcpToColor, l=levelToHex, wl=walkingLevelToHex,
                                           crime_labels=crime_labels,
                                           crime_values=crime_values, crime_levels=crime_levels,
                                           crimeType_labels=crimeType_labels, crimeType_values=crimeType_values,
                                           walking_labels=walking_labels, walking_values=walking_values,
                                           walking_levels=walking_levels, desc_dict=desc_dict,
                                           general_labels=general_labels,
                                           general_values=general_values,url="./main/static/WordCloud.png",
                                           rn=int(r['review_number']),avg_crime_list=avg_list[0:-2], avg_walking_list=avg_list[-2:])
    return render_template('home.html', form=form)


@app.route('/info', methods=['GET', 'POST'])
def info_page():
    if request.method == "GET":
        return redirect(url_for('info_page'))


@app.route('/about', methods=['GET'])
def about_page():
    return render_template('about.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    fdb = pyrebase.initialize_app(firebaseConfig).database()
    res = fdb.child('rankings').order_by_child('name').get().each()
    filtered_dict = [{'name': r.val()['formal_name']} for r in res]

    resp = jsonify(filtered_dict)
    return resp


def get_detailed_data(fdb):
    ref_ranking = fdb.child("rankings").get()
    ref_crime = fdb.child("university_crime").get()
    ref_climate = fdb.child("university_climate").get()
    ref_traffic = fdb.child("university_traffic").get()

    r_ranking = ref_ranking.each()[0]
    header_ranking = list(r_ranking.val().keys())

    r_crime = ref_crime.each()[0]
    header_crime = list(r_crime.val().keys())

    r_climate = ref_climate.each()[0]
    header_climate = list(r_climate.val().keys())

    r_traffic = ref_traffic.each()[0]
    header_traffic = list(r_traffic.val().keys())

    header_raw = header_ranking+header_crime+header_climate+header_traffic
    # header_raw = header_ranking
    header = header_raw[0:1]+header_raw[2:]

    # write into the file
    csv_file = open('./main/data/detailed_data.csv','w',newline='',encoding='utf-8')
    writer = csv.writer(csv_file)
    writer.writerow(header)

    obj_sum = len(ref_ranking.each())
    for i in range(obj_sum):
        ranking_dic = ref_ranking.each()[i].val()
        ranking_data = []
        for r in header_ranking:
            if r in ranking_dic:
                ranking_data.append(ranking_dic[r])
            else:
                ranking_data.append('')
        ranking = ranking_data[0:1] + ranking_data[2:]

        # crime_data = list(ref_crime.each()[i].val().values())
        crime_dic = ref_crime.each()[i].val()
        crime_data = []
        for r in header_crime:
            if r in crime_dic:
                crime_data.append(crime_dic[r])
            else:
                crime_data.append('')

        # climate_data = list(ref_climate.each()[i].val().values())
        climate_dic = ref_climate.each()[i].val()
        climate_data = []
        for r in header_climate:
            if r in climate_dic:
                climate_data.append(climate_dic[r])
            else:
                climate_data.append('')

        # traffic_data = list(ref_traffic.each()[i].val().values())

        traffic_dic = ref_traffic.each()[i].val()
        traffic_data = []
        for r in header_traffic:
            if r in traffic_dic:
                traffic_data.append(traffic_dic[r])
            else:
                traffic_data.append('')

        row = ranking + crime_data + climate_data + traffic_data

        writer.writerow(row)
    csv_file.close()
    return 1

# download details
@app.route('/download_data/<filename>', methods=['GET','POST'])
def download_data(filename):
    '''generate the detailed data'''
    firebase = pyrebase.initialize_app(firebaseConfig)
    fdb = firebase.database()

    # for r in ref_ranking.each():

    get_dt = get_detailed_data(fdb)
    print(get_dt)

    path = os.getcwd()
    data_dir = os.path.join(path,'main/data')
    return send_from_directory(data_dir,filename, as_attachment=True)


def for_email(email):
    path = os.getcwd()
    data_dir = os.path.join(path,'main/data')
    output_list = os.listdir(data_dir)
    print(output_list)
    attachments = []
    expert_email = 'haoqingm@gmail.com'
    # get all the files to send
    if 'email_content.txt' in output_list:
        email_file = os.path.join(data_dir,'email_content.txt')
        attachments.append(email_file)
        content = 'Thank you for visiting UIndex! Your request has beed received. We will contact you as soon as possible.'   
        recipients = email
        subject = 'UIndex Analysis'
        body = content

    # print(attachments)
    msg_u = MIMEMultipart()
    smtpHost = 'smtp.gmail.com'
    sendAddr = 'xiaoyigu1809@gmail.com'
    password = '2022dsci551'
    msg_u['from'] = app.config['MAIL_USERNAME']
    msg_u['to'] = recipients
    msg_u['Subject'] = subject
    txt = MIMEText(content, 'plain', 'utf-8')
    msg_u.attach(txt)
    server = smtplib.SMTP(smtpHost, 587)
    server.ehlo()
    server.starttls()
    # server.set_debuglevel(1)  # can be used to check bugs
    server.login(sendAddr, password)
    server.sendmail(sendAddr, recipients, str(msg_u))

    msg_e = MIMEMultipart()
    msg_e['from'] = app.config['MAIL_USERNAME']
    msg_e['to'] = expert_email
    msg_e['Subject'] = subject
    expert_msg = 'One user has a request. Please contact him/her. Email: '+email
    txt_e = MIMEText(expert_msg, 'plain', 'utf-8')
    msg_e.attach(txt_e)
    server.sendmail(sendAddr, expert_email, str(msg_e))
        # print("\n"+ str(len(filelist)) + "files are successfully sent!")
    server.quit()
    return 1


@app.route('/email_page', methods=['GET','POST'])
def email_page():
    firebase = pyrebase.initialize_app(firebaseConfig)
    fdb = firebase.database()
    form = emailForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        print(email)
        if email:
            print(email)
            fdb.child('emails').child(email)
            email_sent = for_email(email)
            return render_template('submit.html', form=form)
    return render_template('email.html', form=form)
