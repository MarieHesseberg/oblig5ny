from flask import Flask, render_template, request
from database import get_db, init_db, close_connection
import sqlite3

app = Flask(__name__)

# Initialize database
with app.app_context():
    init_db()

# Sample data for barnehager
barnehager = [
    {"barnehage_navn": "Sørlandet Barnehage", "barnehage_antall_plasser": 50, "barnehage_ledige_plasser": 0},
    {"barnehage_navn": "Kristiansand Småbarnssenter", "barnehage_antall_plasser": 30, "barnehage_ledige_plasser": 5},
    {"barnehage_navn": "Blåbærtoppen Barnehage", "barnehage_antall_plasser": 40, "barnehage_ledige_plasser": 20},
    {"barnehage_navn": "Randesund Liten og Stor Barnehage", "barnehage_antall_plasser": 60, "barnehage_ledige_plasser": 3},
    {"barnehage_navn": "Havgløtt Barnehage", "barnehage_antall_plasser": 25, "barnehage_ledige_plasser": 0},
    {"barnehage_navn": "Vågsbygd Skolebarnehage", "barnehage_antall_plasser": 35, "barnehage_ledige_plasser": 12},
    {"barnehage_navn": "Fjordglimt Barnehage", "barnehage_antall_plasser": 45, "barnehage_ledige_plasser": 0},
    {"barnehage_navn": "Kilden Barn og Lek", "barnehage_antall_plasser": 55, "barnehage_ledige_plasser": 25},
    {"barnehage_navn": "Eventyrhuset Barnehage", "barnehage_antall_plasser": 20, "barnehage_ledige_plasser": 1},
    {"barnehage_navn": "Trollstua Barnehage", "barnehage_antall_plasser": 38, "barnehage_ledige_plasser": 4}
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/apply')
def apply():
    return render_template('sok.html')

@app.route('/kindergartens')
def kindergartens():
    return render_template('barnehager.html', data=barnehager)

@app.route('/applications')
def applications():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT navn_forelder_1, prioriterte_barnehager, resultat, valgt_barnehage FROM soknader')

    soknader = []
    for row in cursor.fetchall():
        row_dict = dict(row)
        
        if 'prioriterte_barnehager' in row_dict and row_dict['prioriterte_barnehager']:
            row_dict['prioriterte_barnehager'] = row_dict['prioriterte_barnehager'].split(',')
        
        soknader.append(row_dict)
    return render_template('soknader.html', soknader=soknader)

@app.route('/statistikk', methods=['GET'])
def statistikk():
    try:
        import matplotlib.pyplot as plt
        import io
        import base64

        # Data for Kristiansand (example values)
        years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
        values = [78, 79.5, 79.1, 80.1, 81.6, 80.9, 84.5, 84.1, 85.2]

        # Generate plot
        plt.figure(figsize=(10, 6))
        plt.plot(years, values, marker='o', linestyle='-', color='b', label='Kristiansand')
        plt.title('Prosentandel barn i barnehage (1-2 år) - Kristiansand')
        plt.xlabel('År')
        plt.ylabel('Prosentandel')
        plt.xticks(years, rotation=45)
        plt.grid(True)
        plt.legend()

        # Save the plot to a string buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode()
        buf.close()

        # Embed the image in the HTML response
        plot_url = 'data:image/png;base64,{}'.format(plot_data)
        return render_template('statistikk.html', plot_url=plot_url)

    except Exception as e:
        # Log error details
        print(f"Error generating statistics: {e}")
        return f"An error occurred: {e}", 500


@app.route('/commit', methods=['GET'])
def commit():
    db = get_db()
    db.row_factory = sqlite3.Row
    cursor = db.execute('SELECT * FROM soknader')
    all_soknader = cursor.fetchall()
    return render_template('commit.html', soknader=all_soknader)


@app.route('/behandle', methods=['POST'])
def behandle():
    # Gather data from the form submission
    navn_forelder_1 = request.form.get('navn_forelder_1')
    barnehage_prioritet_1 = request.form.get('barnehage_prioritet_1')
    barnehage_prioritet_2 = request.form.get('barnehage_prioritet_2')
    barnehage_prioritet_3 = request.form.get('barnehage_prioritet_3')
    tidspunkt_oppstart = request.form.get('tidspunkt_oppstart')

    fortrinnsrett_barnevern = request.form.get('fortrinnsrett_barnevern')
    fortrinnsrett_sykdom_familie = request.form.get('fortrinnsrett_sykdom_familie')
    fortrinnsrett_sykdom_barn = request.form.get('fortrinnsrett_sykdom_barn')

    # Check fortrinnsrett
    fortrinnsrett = any([fortrinnsrett_barnevern, fortrinnsrett_sykdom_familie, fortrinnsrett_sykdom_barn])

    # Handle barnehage prioritization and availability
    valgt_barnehage = None
    resultat = "AVSLAG"
    prioriteter = [barnehage_prioritet_1, barnehage_prioritet_2, barnehage_prioritet_3]

    for prioritet in prioriteter:
        for barnehage in barnehager:
            if barnehage["barnehage_navn"] == prioritet:
                if fortrinnsrett:
                    if barnehage["barnehage_ledige_plasser"] > 0:
                        valgt_barnehage = prioritet
                        barnehage["barnehage_ledige_plasser"] -= 1
                        resultat = "TILBUD"
                        break
                else:
                    if barnehage["barnehage_ledige_plasser"] > 3:
                        valgt_barnehage = prioritet
                        barnehage["barnehage_ledige_plasser"] -= 1
                        resultat = "TILBUD"
                        break
        if valgt_barnehage:
            break

    # Insert application data into the database
    db = get_db()
    db.execute(
        'INSERT INTO soknader (navn_forelder_1, prioriterte_barnehager, resultat, valgt_barnehage, tidspunkt_oppstart) VALUES (?, ?, ?, ?, ?)',
        (navn_forelder_1, ', '.join([barnehage_prioritet_1, barnehage_prioritet_2, barnehage_prioritet_3]), resultat, valgt_barnehage, tidspunkt_oppstart)
    )
    db.commit()

    # Prepare data for response
    data = {
        "resultat": resultat,
        "prioriteter": [barnehage_prioritet_1, barnehage_prioritet_2, barnehage_prioritet_3],
        "valgt_barnehage": valgt_barnehage,
        "tidspunkt_oppstart": tidspunkt_oppstart
    }
    return render_template('svar.html', data=data)


# Close database connection
app.teardown_appcontext(close_connection)

if __name__ == '__main__':
    app.run()
