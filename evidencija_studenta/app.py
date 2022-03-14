#Unosenje potrebnih biblioteka
from operator import indexOf
from flask import Flask, render_template, url_for, request, redirect, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
import ast
import os
from flask_mail import Mail, Message
import io
import csv

# za bazu podataka
import mysql.connector
import mariadb

konekcija = mysql.connector.connect(
    host="localhost",
    username="root",
    password="",
    database="evidencija_studenata",
)
kursor = konekcija.cursor(dictionary=True)

#Deklaracija Flask aplikacije
app = Flask(__name__)
app.secret_key = "tajni_kljuc_aplikacije" # koji nije toliko tajni

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = ""
app.config["MAIL_PASSWORD"] = ""
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

# deklaracija upload direktorijuma
UPLOAD_FOLDER = "static/uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

#********************************************************************************
#Logika aplikacije
#********************************************************************************
# GLOBALNE FUNKCIJE
def ulogovan():
    if "ulogovani_korisnik" in session:
        return True
    else:
        return False

def rola():
    if ulogovan():
        return ast.literal_eval(session["ulogovani_korisnik"]).pop("rola")

def send_email(ime, prezime, email, lozinka):
    msg = Message(
        subject = "Korisnicki nalog",
        sender = "ATVSS Evidencija studenata",
        recipients = [email],
    )
    msg.html = render_template("email.html", ime=ime, prezime=prezime, lozinka=lozinka)
    mail.send(msg)
    return "Sent"


def getUserId():
    user = ast.literal_eval(session["ulogovani_korisnik"])
    if user.get('rola') == 'student':
        upit = "SELECT id FROM studenti WHERE email=%s"
        vrednost = (user.get('email'),)
        kursor.execute(upit, vrednost)
        rezId = kursor.fetchone()
        return rezId.get('id')
    else:
        upit = "SELECT id FROM korisnici WHERE email=%s"
        vrednost = (user.get('email'),)
        kursor.execute(upit, vrednost)
        rezId = kursor.fetchone()
        return rezId.get('id')

#********************************************************************************
# login / logout
#********************************************************************************
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        forma = request.form
        upit = "SELECT * FROM korisnici WHERE email=%s"
        vrednost = (forma["email"],)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        if check_password_hash(korisnik["lozinka"], forma["lozinka"]):
            # upisivanje korisnika u sesiju
            session["ulogovani_korisnik"] = str(korisnik)
            return redirect(url_for("studenti"))
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("ulogovani_korisnik", None)
    return redirect(url_for("login"))
#********************************************************************************
# SVE ZA KORISNIKE
#********************************************************************************
@app.route("/korisnici", methods=["GET"])
def korisnici():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        broj_prikaza = 5
        strana = request.args.get('page', '1')
        offset = int(strana) * broj_prikaza - broj_prikaza
        prethodna_strana = ""
        sledeca_strana = "/korisnici?page=2"

        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            sledeca_strana = "=".join(split_path)
            breakpage = sledeca_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            sledeca_strana = breakpage[0] + 'page=' + str(int(strana) + 1) + '&' + '&'.join(half2)
               
            prethodna_strana = "=".join(split_path)
            breakpage = prethodna_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            prethodna_strana = breakpage[0] + 'page=' + str(int(strana) - 1) + '&' + '&'.join(half2)

        args = request.args.to_dict()
        order_by = 'id'
        order_type = 'asc'
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = 'desc'

        k_ime = "%%"
        k_prezime = "%%"
        k_email = "%%"
        k_rola = "%%"

        if "ime" in args:
            k_ime = '%' + args["ime"] + '%'
        if "prezime" in args:
            k_prezime = '%' + args["prezime"] + '%'
        if "rola" in args:
            k_rola = '%' + args["rola"] + '%'

        upit = f"""
            SELECT * FROM korisnici WHERE ime LIKE "{k_ime}" AND
            prezime LIKE "{k_prezime}" AND
            rola LIKE "{k_rola}"
            ORDER BY {order_by} {order_type}
            LIMIT {broj_prikaza} OFFSET {offset}
        """

        kursor.execute(upit)
        korisnici = kursor.fetchall()
        return render_template("korisnici.html", korisnici=korisnici, strana=strana, sledeca_strana=sledeca_strana, prethodna_strana=prethodna_strana, order_type=order_type, args=args)
    else:
        return redirect(url_for('login'))

@app.route("/korisnik_novi", methods=["GET","POST"])
def korisnik_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            return render_template("korisnik_novi.html")
        elif request.method == "POST":
            forma = request.form
            # hesujemo lozinku kako ne bi bila lako vidljiva
            hesovana_lozinka = generate_password_hash(forma["lozinka"])
            # tuple vrednosti forme
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                forma["rola"],
                hesovana_lozinka,
            )
            # SQL upit
            upit = """
                INSERT INTO
                korisnici(ime, prezime, email, rola, lozinka)
                VALUES (%s, %s, %s, %s, %s)
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()

            send_email(forma["ime"], forma["prezime"], forma["email"], forma["lozinka"])

            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))

@app.route("/korisnik_izmena/<id>", methods=["GET","POST"])
def korisnik_izmena(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM korisnici WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            korisnik = korisnik = kursor.fetchone()
            return render_template("korisnik_izmena.html", korisnik=korisnik)
        elif request.method == "POST":
            upit = """UPDATE korisnici SET
                ime=%s,
                prezime=%s,
                email=%s,
                rola=%s,
                lozinka=%s
                WHERE id=%s
            """
            forma = request.form
            hesovana_lozinka = generate_password_hash(forma["lozinka"])
            vrednosti = (
                forma["ime"],
                forma["prezime"],
                forma["email"],
                forma["rola"],
                hesovana_lozinka,
                id,
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()
            return redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))

@app.route("/korisnik_brisanje/<id>", methods=["POST"])
def korisnik_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        # Brisanje studenta iz liste kada se brise korisnik
        upit = "SELECT * FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        korisnik = kursor.fetchone()
        if korisnik['rola'] == 'student':
            upit = "SELECT id FROM studenti WHERE ime LIKE %s AND prezime LIKE %s AND email LIKE %s"
            vrednosti = (korisnik['ime'], korisnik['prezime'], korisnik['email'],)
            kursor.execute(upit, vrednosti)
            studentId = kursor.fetchone()
            
            upit = "DELETE FROM studenti WHERE id=%s"
            vrednost = (studentId['id'],)
            kursor.execute(upit, vrednost)
            konekcija.commit()

        upit = "DELETE FROM korisnici WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        return redirect(url_for("korisnici"))
    else:
        return redirect(url_for('login'))

#  KRAJ SVE ZA KORISNIKE
#********************************************************************************
# SVE ZA PREDMETE
#********************************************************************************
@app.route("/predmeti", methods=["GET"])
def predmeti():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        broj_prikaza = 5
        strana = request.args.get('page', '1')
        offset = int(strana) * broj_prikaza - broj_prikaza
        prethodna_strana = ""
        sledeca_strana = "/predmeti?page=2"

        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            sledeca_strana = "=".join(split_path)
            breakpage = sledeca_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            sledeca_strana = breakpage[0] + 'page=' + str(int(strana) + 1) + '&' + '&'.join(half2)
               
            prethodna_strana = "=".join(split_path)
            breakpage = prethodna_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            prethodna_strana = breakpage[0] + 'page=' + str(int(strana) - 1) + '&' + '&'.join(half2)

        args = request.args.to_dict()
        order_by = 'id'
        order_type = 'asc'
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = 'desc'

        p_sifra = "%%"
        p_naziv = "%%"
        p_godina_studija = "%%"
        p_obavezni_izborni = "%%"
        if "sifra" in args:
            p_sifra = '%' + args["sifra"] + '%'
        if "naziv" in args:
            p_naziv = '%' + args["naziv"] + '%'
        if "godina_studija" in args:
            p_godina_studija = '%' + args["godina_studija"] + '%'
        if "obavezni_izborni" in args:
            p_obavezni_izborni = '%' + args["obavezni_izborni"] + '%'
        
        upit = f"""
            SELECT * FROM predmeti WHERE sifra LIKE "{p_sifra}" AND
            naziv LIKE "{p_naziv}" AND
            godina_studija LIKE "{p_godina_studija}" AND
            obavezni_izborni LIKE "{p_obavezni_izborni}"
            ORDER BY {order_by} {order_type}
            LIMIT {broj_prikaza} OFFSET {offset}
        """

        kursor.execute(upit)
        predmeti = kursor.fetchall()
        return render_template("predmeti.html", predmeti=predmeti, strana=strana, sledeca_strana=sledeca_strana, prethodna_strana=prethodna_strana, order_type=order_type, args=args)
    else:
        return redirect(url_for('login'))

@app.route("/predmet_novi", methods=["GET", "POST"])
def predmet_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            return render_template("predmet_novi.html")
        elif request.method == "POST":
            forma = request.form
            vrednosti = (
                forma["sifra"],
                forma["naziv"],
                forma["godina_studija"],
                forma["espb"],
                forma["obavezni_izborni"],
            )
            # SQL upit
            upit = """
                INSERT INTO
                predmeti(sifra, naziv, godina_studija, espb, obavezni_izborni)
                VALUES (%s, %s, %s, %s, %s)
            """
            kursor.execute(upit, vrednosti)
            konekcija.commit()
            return redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))

@app.route("/predmet_izmena/<id>", methods=["GET","POST"])
def predmet_izmena(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM predmeti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            predmet = kursor.fetchone()
            return render_template("predmet_izmena.html", predmet=predmet)
        elif request.method == "POST":
            upit = """UPDATE predmeti SET
                sifra=%s,
                naziv=%s,
                godina_studija=%s,
                espb=%s,
                obavezni_izborni=%s
                WHERE id=%s
            """
            forma = request.form
            vrednosti = (
                forma["sifra"],
                forma["naziv"],
                forma["godina_studija"],
                forma["espb"],
                forma["obavezni_izborni"],
                id,
            )
            kursor.execute(upit,vrednosti)
            konekcija.commit()
            return redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))


@app.route("/predmet_brisanje/<id>", methods=["POST"])
def predmet_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        upit = """
            DELETE FROM predmeti WHERE id=%s
        """
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()
        return redirect(url_for("predmeti"))
    else:
        return redirect(url_for('login'))

# KRAJ SVE ZA PREDMETE
#********************************************************************************
# SVE ZA STUDENTE
#********************************************************************************
@app.route("/studenti", methods=["GET"])
def studenti():
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        broj_prikaza = 5
        strana = request.args.get('page', '1')
        offset = int(strana) * broj_prikaza - broj_prikaza
        prethodna_strana = ""
        sledeca_strana = "/studenti?page=2"

        if "=" in request.full_path:
            split_path = request.full_path.split("=")
            sledeca_strana = "=".join(split_path)
            breakpage = sledeca_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            sledeca_strana = breakpage[0] + 'page=' + str(int(strana) + 1) + '&' + '&'.join(half2)
               
            prethodna_strana = "=".join(split_path)
            breakpage = prethodna_strana.split("page=")
            half2 = breakpage[1].split('&')
            del half2[0]
            prethodna_strana = breakpage[0] + 'page=' + str(int(strana) - 1) + '&' + '&'.join(half2)


        args = request.args.to_dict()
        order_by = 'id'
        order_type = 'asc'
        if "order_by" in args:
            order_by = args["order_by"].lower()
            if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                if args["order_type"] == "asc":
                    order_type = 'desc'

        s_ime = "%%"
        s_prezime = "%%"
        s_broj_indeksa = "%%"
        s_godina_studija = "%%"
        s_espb_od = '0'
        s_espb_do = '240'
        s_prosek_ocena_od = '0'
        s_prosek_ocena_do = '10'
        if "ime" in args:
            s_ime = '%' + args["ime"] + '%'
        if "prezime" in args:
            s_prezime = '%' + args["prezime"] + '%'
        if "broj_indeksa" in args:
            s_broj_indeksa = '%' + args["broj_indeksa"] + '%'
        if "godina_studija" in args:
            s_godina_studija = '%' + args["godina_studija"] + '%'
        if "prosek_ocena_od" in args and args['prosek_ocena_od'] != '':
            s_prosek_ocena_od = args["prosek_ocena_od"]
        if "prosek_ocena_do" in args and args['prosek_ocena_od'] != '':
            s_prosek_ocena_do = args["prosek_ocena_do"]

        #temp fix for order_by broj_indeksa
        if order_by == "broj_indeksa":
            order_by = 'ABS(' + order_by + ')'

        upit = f"""
            SELECT * FROM studenti WHERE ime LIKE '{s_ime}' AND
            prezime LIKE '{s_prezime}' AND
            broj_indeksa LIKE '{s_broj_indeksa}' AND
            godina_studija LIKE '{s_godina_studija}' AND
            espb >= {s_espb_od} AND espb <= {s_espb_do} AND
            prosek_ocena >= '{s_prosek_ocena_od}' AND prosek_ocena <= '{s_prosek_ocena_do}'
            ORDER BY {order_by} {order_type}
            LIMIT {broj_prikaza} OFFSET {offset}
        """

        kursor.execute(upit)
        studenti = kursor.fetchall()

        return render_template("studenti.html", studenti=studenti, rola=rola(), strana=strana, sledeca_strana=sledeca_strana, prethodna_strana=prethodna_strana, order_type=order_type, args=args)
    else:
        return redirect(url_for('login'))

@app.route("/student_novi", methods=["GET", "POST"])
def student_novi():
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            return render_template("student_novi.html")
        elif request.method == "POST":
            forma = request.form
            # za slike
            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["jmbg"] + file.filename 
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

            vrednosti = (
                forma["broj_indeksa"],
                forma["ime"],
                forma["ime_roditelja"],
                forma["prezime"],
                forma["email"],
                forma["broj_telefona"],
                forma["godina_studija"],
                forma["datum_rodjenja"],
                forma["jmbg"],
                naziv_slike,
            )
            # SQL upit
            upit = """
                INSERT INTO
                studenti(broj_indeksa, ime, ime_roditelja, prezime, email, broj_telefona, godina_studija, datum_rodjenja, jmbg, slika)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            kursor.execute(upit, vrednosti)
            konekcija.commit()

            #Automatsko kreiranje naloga za studenta
            student_sifra = generate_password_hash('VTS_' + forma["broj_indeksa"])
            vrednosti = (forma["ime"], forma["prezime"], forma["email"], student_sifra, 'student')
            upit = """
                INSERT INTO
                korisnici(ime, prezime, email, lozinka, rola)
                VALUES (%s, %s, %s, %s, %s)
            """
            kursor.execute(upit, vrednosti)        
            konekcija.commit()

            return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))

@app.route("/student_izmena/<id>", methods=["GET","POST"])
def student_izmena(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if(rola() == 'student' and int(id) != int(getUserId())):
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            upit = "SELECT * FROM studenti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            student = kursor.fetchone()

            return render_template("student_izmena.html", student=student)
        elif request.method == "POST":
            forma = request.form
            # slika
            naziv_slike = ""
            if "slika" in request.files:
                file = request.files["slika"]
                if file.filename:
                    naziv_slike = forma["jmbg"] + file.filename 
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], naziv_slike))

            # kad se menja studenta menja se i u bazi za korisnike
            upit = "SELECT * FROM studenti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            student = kursor.fetchone()

            upit = "SELECT id FROM korisnici WHERE ime LIKE %s AND prezime LIKE %s AND email like %s"
            vrednosti = (student['ime'], student['prezime'], student['email'],)
            kursor.execute(upit, vrednosti)
            old_id = kursor.fetchone()

            upit = """UPDATE studenti SET
                ime=%s,
                ime_roditelja=%s,
                prezime=%s,
                broj_indeksa=%s,
                godina_studija=%s,
                jmbg=%s,
                datum_rodjenja=%s,            
                broj_telefona=%s,
                email=%s,
                slika=%s
                WHERE id=%s
            """

            vrednosti = (
                forma["ime"],
                forma["ime_roditelja"],
                forma["prezime"],
                forma["broj_indeksa"],
                forma["godina_studija"],
                forma["jmbg"],
                forma["datum_rodjenja"],
                forma["broj_telefona"],
                forma["email"],
                naziv_slike,
                id,
            )
            kursor.execute(upit, vrednosti)
            konekcija.commit()

            upit = "UPDATE korisnici SET ime=%s, prezime=%s, email=%s WHERE id=%s"
            vrednosti = (forma['ime'], forma['prezime'], forma['email'], old_id['id'])
            kursor.execute(upit, vrednosti)
            konekcija.commit()

            return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))

@app.route("/student_brisanje/<id>", methods=["POST"])
def student_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        # Kada brisemo studenta brise se iz korisnika
        upit = "SELECT * FROM studenti WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        student = kursor.fetchone()

        upit = "SELECT id FROM korisnici WHERE ime LIKE %s AND prezime LIKE %s AND email LIKE %s"
        vrednosti = (student['ime'], student['prezime'], student['email'],)
        kursor.execute(upit, vrednosti)
        Id_za_brisanje = kursor.fetchone()

        upit = """
            DELETE FROM studenti WHERE id=%s
        """
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()

        upit = "DELETE FROM korisnici WHERE id=%s"
        vrednost = (Id_za_brisanje['id'],)
        kursor.execute(upit, vrednost)
        konekcija.commit()

        return redirect(url_for("studenti"))
    else:
        return redirect(url_for('login'))

@app.route("/student/<id>", methods=["GET","POST"])
def student(id):
    if(rola() == 'student' and int(id) != int(getUserId())):
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        if request.method == "GET":
            # Racunanje proseka ocena
            upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            prosek_ocena = kursor.fetchone()

            # Racunanje ukupnih espb
            upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            espb = kursor.fetchone()

            # Izmena tabele studenti
            upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
            vrednosti = (
                espb["rezultat"],
                prosek_ocena["rezultat"],
                id
            )
            kursor.execute(upit, vrednosti)

            # Dodatak za filtriranje i sortiranje :(
            """
            broj_prikaza = 5
            strana = request.args.get('page', '1')
            offset = int(strana) * broj_prikaza - broj_prikaza
            prethodna_strana = ""
            sledeca_strana = f"/student/{id}?page=2"

            if "=" in request.full_path:
                split_path = request.full_path.split("=")
                sledeca_strana = "=".join(split_path)
                breakpage = sledeca_strana.split("page=")
                half2 = breakpage[1].split('&')
                del half2[0]
                sledeca_strana = breakpage[0] + 'page=' + str(int(strana) + 1) + '&' + '&'.join(half2)
                
                prethodna_strana = "=".join(split_path)
                breakpage = prethodna_strana.split("page=")
                half2 = breakpage[1].split('&')
                del half2[0]
                prethodna_strana = breakpage[0] + 'page=' + str(int(strana) - 1) + '&' + '&'.join(half2)
            """

            args = request.args.to_dict()
            order_by = 'sifra'
            order_type = 'asc'
            if "order_by" in args:
                order_by = args["order_by"].lower()
                if ("prethodni_order_by" in args and args["prethodni_order_by"] == args["order_by"]):
                    if args["order_type"] == "asc":
                        order_type = 'desc'

            st_sifra = "%%"
            st_naziv = "%%"
            st_godina_studija = "%%"
            st_obavezni_izborni = "%%"
            st_ocena_od = '0'
            st_ocena_do = '10'
            if "sifra" in args:
                st_sifra = '%' + args["sifra"] + '%'
            if "naziv" in args:
                st_naziv = '%' + args["naziv"] + '%'
            if "godina_studija" in args:
                st_godina_studija = '%' + args["godina_studija"] + '%'
            if "ocena_od" in args and args['ocena_od'] != '':
                st_ocena_od = args["ocena_od"]
            if "ocena_do" in args and args['ocena_do'] != '':
                st_ocena_do = args["ocena_do"]
            if "obavezni_izborni" in args:
                st_obavezni_izborni = '%' + args["obavezni_izborni"] + '%'


            # ..
            upit = "SELECT * FROM studenti WHERE id=%s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            student = kursor.fetchone()

            upit = "SELECT * FROM predmeti"
            kursor.execute(upit)
            predmeti = kursor.fetchall()

            upit = "SELECT * FROM ocene WHERE student_id=%s"
            kursor.execute(upit, vrednost)
            ocene = kursor.fetchall()

            upit = f"""
                SELECT * FROM ocene oc INNER JOIN predmeti pred ON pred.id=oc.predmet_id WHERE student_id={id} AND
                sifra LIKE '{st_sifra}' AND
                naziv LIKE '{st_naziv}' AND
                godina_studija LIKE '{st_godina_studija}' AND
                ocena >= '{st_ocena_od}' AND ocena <= '{st_ocena_do}' AND
                obavezni_izborni LIKE '{st_obavezni_izborni}'
                ORDER BY {order_by} {order_type}
                LIMIT 5 OFFSET 0
            """
            kursor.execute(upit)
            procene = kursor.fetchall()
            

            return render_template("student.html", student=student, predmeti=predmeti, procene=procene, ocene=ocene, rola=rola(), order_type=order_type, args=args)
    else:
        return redirect(url_for('login'))

@app.route("/ocena_nova/<id>", methods=["POST"])
def ocena_nova(id):
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        # Dodavanje u tablu ocene
        upit = """
            INSERT INTO ocene(student_id, predmet_id, ocena, datum)
            VALUES(%s, %s, %s, %s)
        """
        forma = request.form
        vrednosti = (
            id,
            forma["predmet_id"],
            forma["ocena"],
            forma["datum"]
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        # Racunanje proseka ocena
        upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        prosek_ocena = kursor.fetchone()

        # Racunanje ukupnih espb
        upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        espb = kursor.fetchone()

        # Izmena tabele studenti
        upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
        vrednosti = (
            espb["rezultat"],
            prosek_ocena["rezultat"],
            id
        )
        kursor.execute(upit, vrednosti)
        konekcija.commit()

        return redirect(url_for("student", id=id))
    else:
        return redirect(url_for('login'))

@app.route("/ocena_brisanje/<id>", methods=["POST"])
def ocena_brisanje(id):
    if rola() == "profesor":
        return redirect(url_for("studenti"))
    if rola() == "student":
        return redirect(url_for("student", id=getUserId()))
    if ulogovan():
        upit = "SELECT student_id FROM ocene WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        student_id = kursor.fetchone()
        id_studenta = student_id.get("student_id")

        upit = "DELETE FROM ocene WHERE id=%s"
        vrednost = (id,)
        kursor.execute(upit, vrednost)
        konekcija.commit()

        return redirect(url_for("student", id=id_studenta))
    else:
        return redirect(url_for('login'))

# KRAJ SVE ZA STUDENTE
#********************************************************************************
@app.route("/export/<tip>/<id>")
def export(tip, id):
    switch = {
        "studenti": "SELECT * FROM studenti",
        "korisnici": "SELECT * FROM korisnici",
        "predmeti": "SELECT * FROM predmeti",
        "student": f"SELECT pred.naziv, oc.ocena, pred.espb, pred.godina_studija, pred.obavezni_izborni pred FROM ocene oc INNER JOIN predmeti pred ON pred.id=oc.predmet_id WHERE student_id={id}",
    }
    upit = switch.get(tip)

    kursor.execute(upit)
    rezultat = kursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    for row in rezultat:
        red = []
        for value in row.values():
            red.append(str(value))
        writer.writerow(red)

    output.seek(0)

    return Response(
        output,
        mimetype = "text/csv",
        headers = {"Content-Disposition": "attachment;filename=" + tip + ".csv"},
    )

"""
@app.route("/pwd_change/<id>", methods=['GET', 'POST'])
def pwd_change(id):
    if(int(id) != int(getUserId())):
        return redirect(url_for("pwd_change", id=getUserId()))
    if ulogovan():
        if request.method == 'GET':
            return render_template('pwd_change.html', id=id)
        elif request.method == 'POST':
            forma = request.form
            upit = "SELECT lozinka FROM korisnici WHERE id LIKE %s"
            vrednost = (id,)
            kursor.execute(upit, vrednost)
            trenutna_sifra = kursor.fetchone()
            if check_password_hash(forma["pwd_stara"], trenutna_sifra):
                if(forma['pwd1'] == forma['pwd2']):
                    hesovana_lozinka = generate_password_hash(forma["pwd1"])
                    upit = "UPDATE korisnici SET lozinka=%s WHERE id=%s"
                    kursor.execute(upit, id)
                    konekcija.commit()
                    print("promenjenja sifra")
                    return render_template("login.html")
"""

    

#********************************************************************************
#pokretanje aplikacije
app.run(debug=True)
