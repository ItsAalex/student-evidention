from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash 
import mariadb
import mysql.connector

konekcija = mysql.connector.connect(
    passwd="", # lozinka za bazu
    user="root", # korisničko ime
    database="evidencija2", # ime baze     
    port=3306, # port na kojem je mysql server 
    auth_plugin='mysql_native_password' # ako se koristi mysql 8.x  
) 
kursor = konekcija.cursor(dictionary=True) # kursor = promenljiva koja nam sluzi da se povezemo sa bazom, nad njom izvrsavamo upite
                                           #(veza izmedju app i baze)

#deklaracija aplikacije
app = Flask(__name__)

#logika aplikacije
@app.route('/', methods=['GET'])

def render_login():
    return render_template('login.html')

@app.route('/proba/<id>', methods=['GET','POST'])
def render_primer(id)-> 'html':
    return render_template('primer.html')

@app.route('/korisnici', methods=['GET'])

def render_korisnici():
    upit = "select * from korisnici"
    kursor.execute(upit) #ovako izvrsavamo upit koji smo zadali
    korisnici = kursor.fetchall() # da nam unese u promenljivu vrednost koja je vracena
    return render_template('korisnici.html', korisnici = korisnici) # promenljiva korisnici koja je parametar ce dobiti vrednost iz gornje
                                                                    # promenljive korisnici

@app.route('/korisnik-novi', methods=['GET','POST']) #GET zato sto ce da nam se vrati neka nova stranica, 
                                                      # POST zato sto cemo u toj novoj stranici moci da dodajemo nove podatke na srv.
def korisnik_novi():
    if request.method == "GET":
        return render_template('korisnik-novi.html')

    if request.method == "POST":
        forma = request.form       #promenljiva "forma" sluzi da uzmemo podatke iz forme
                                   #na ovaj nacin ce nasa promenljiva forma uzeti iz forme cija je metoda post uzece input sa name-om "ime" 
        hesovana_lozinka = generate_password_hash(forma["lozinka"]) 
        vrednosti =(                                            
            forma["ime"],   #ovaj nacin ce nasa promenljiva forma uzeti iz forme cija je metoda post uzece input sa name-om "ime"  
            forma["prezime"],
            forma["email"],
            forma["rola"],
            hesovana_lozinka #vrednosti koje kasnije zelim da saljem u bazu da bih dodao novog korisnika radim unutar tuple-a.
        )

        #triple navodnike stavljamo kada string zelimo da pisemo u vise redova
        #insert into - naredba za dodavanje novih stvari
        # ovi %s ce kasnije da uzimaju vrednosti iz ovog "vrednosti tuple-a" koji se nalazi iznad. Ime za ime.. itd...
        upit = """ insert into
            korisnici(ime, prezime, email, rola, lozinka)
            values (%s, %s, %s, %s, %s)
        """ 
        kursor.execute(upit, vrednosti) #izvrsavanje upita koji smo zadali part 2.
        konekcija.commit() # ovako sacuvavamo podatke u bazi koje smo dodali

        #konacno kada dodamo podatke, mozemo kao na poziv funkcije redirekt vratiti novu stranicu sa unesenim podacima
        return redirect(url_for("render_korisnici"))

@app.route('/korisnik-izmena/ <id>', methods=['GET','POST'])  #ovo ovde <id> mora da se nadje kao parametar funkcije ispod
def korisnik_izmena(id):
    if request.method == "GET":
        upit = "select * from korisnici where id=%s" #prosledjivanje vrednosti putem tupla (%s) (u nastavku koda)
        vrednost = (id, ) # TRIK ZA DEFINISANJE TUPLA S JEDNOM VREDNOSCU! VAZNO I ZA TEST
        kursor.execute(upit,vrednost) # ovo %s ce se zameniti sa id iz "vrednost" tupla.
        korisnik = kursor.fetchone()  #one jer hvata samo 1 vrednost
        return render_template('korisnik_izmena.html', korisnik = korisnik) # zahvaljujuci korisniku zna ce sta treba gde da popunjava

    if request.method == "POST":
        upit = """UPDATE korisnici SET
                    ime=%s, prezime=%s, email=%s, rola=%s, lozinka=%s 
                    WHERE id= %s     
            """ 
        forma = request.form 
        vrednosti = (         
            forma["ime"],         
            forma["prezime"],         
            forma["email"],        
            forma["rola"],         
            forma["lozinka"],         
            id  #uzima se iz parametra funkcije
        ) 
        kursor.execute(upit, vrednosti) 
        konekcija.commit() 
        return redirect(url_for("render_korisnici")) 

@app.route("/korisnik_brisanje/<id>", methods=["POST"]) #ovde imamo samo POST metodu!
def korisnik_brisanje(id): 
        upit = """ DELETE FROM korisnici WHERE id=%s
        """         
        vrednost = (id,)         
        kursor.execute(upit, vrednost)         
        konekcija.commit()         
        return redirect(url_for("render_korisnici")) 



#pokreni aplikaciju
app.run(debug = True)
