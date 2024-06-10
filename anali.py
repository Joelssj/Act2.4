from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

TOKENS = {
    'PR': r'\b(for|if|else|while|return)\b',
    'ID': r'\b[a-zA-Z_][a-zA-Z_0-9]*\b',
    'NUM': r'\b\d+\b',
    'SYM': r'[;{}()\[\]=<>!+-/*]',
    'ERR': r'.'
}

html_template = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Analizador Léxico, Sintáctico y Semántico</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background-color: #f4f4f9;
      }
      .container {
        width: 80%;
        margin: auto;
        overflow: hidden;
      }
      header {
        background: #333;
        color: #fff;
        padding-top: 30px;
        min-height: 70px;
        border-bottom: #0779e4 3px solid;
      }
      header a {
        color: #fff;
        text-decoration: none;
        text-transform: uppercase;
        font-size: 16px;
      }
      header ul {
        padding: 0;
        list-style: none;
        display: flex;
        justify-content: flex-end;
      }
      header li {
        margin-left: 20px;
      }
      #main-content {
        padding: 30px;
        background: #fff;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
      }
      textarea {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin-bottom: 10px;
      }
      input[type="submit"] {
        background: #0779e4;
        color: #fff;
        border: 0;
        padding: 10px 15px;
        cursor: pointer;
        border-radius: 5px;
      }
      table {
        width: 100%;
        margin-bottom: 20px;
        border-collapse: collapse;
      }
      table, th, td {
        border: 1px solid #ccc;
      }
      th, td {
        padding: 10px;
        text-align: left;
      }
      th {
        background: #0779e4;
        color: #fff;
      }
    </style>
  </head>
  <body>
    <header>
      <div class="container">
        <h1>Analizador Léxico, Sintáctico y Semántico</h1>
      </div>
    </header>
    <div id="main-content" class="container">
      <form method="post">
        <textarea name="code" rows="10" cols="50">{{ code }}</textarea><br>
        <input type="submit" value="Analizar">
      </form>
      <h2>Analizador Léxico</h2>
      <table>
        <tr>
          <th>Tokens</th><th>PR</th><th>ID</th><th>Números</th><th>Símbolos</th><th>Error</th>
        </tr>
        {% for row in lexical %}
        <tr>
          <td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td>
        </tr>
        {% endfor %}
        <tr>
          <td>Total</td><td>{{ total['PR'] }}</td><td>{{ total['ID'] }}</td><td>{{ total['NUM'] }}</td><td>{{ total['SYM'] }}</td><td>{{ total['ERR'] }}</td>
        </tr>
      </table>
      <h2>Analizador Sintáctico y Semántico</h2>
      <table>
        <tr>
          <th>Sintáctico</th><th>Semántico</th>
        </tr>
        <tr>
          <td>{{ syntactic }}</td><td>{{ semantic }}</td>
        </tr>
      </table>
      <h2>Código Corregido</h2>
      <pre>{{ corrected_code }}</pre>
    </div>
  </body>
</html>
'''

def analyze_lexical(code):
    results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    for line in code.split('\n'):
        row = [''] * 6
        for token_name, token_pattern in TOKENS.items():
            for match in re.findall(token_pattern, line):
                results[token_name] += 1
                row[list(TOKENS.keys()).index(token_name)] = 'x'
        rows.append(row)
    return rows, results

def correct_syntactic(code):
    corrected_code = re.sub(r'\bfor\s*\(\s*.*\s*\)\s*\{', r'for (int i = 1; i <= 19; i++) {', code)
    corrected_code = re.sub(r'\{.*\}', r'{\n    System.out.println("hola");\n}', corrected_code, flags=re.DOTALL)
    return corrected_code

def correct_semantic(code):
    corrected_code = re.sub(r'\bSystem\.out\.println\s*\(.*\)\s*;', r'System.out.println("hola");', code)
    return corrected_code

def analyze_syntactic(code):
    corrected_code = code
    errors = []

    if not re.search(r'\bfor\s*\(\s*int\s+\w+\s*=\s*\d+\s*;\s*\w+\s*<=\s*\d+\s*;\s*\w+\+\+\s*\)\s*\{', code):
        errors.append("Error en la sintaxis del bucle 'for'. Asegúrate de declarar el tipo de variable correctamente, por ejemplo: 'for (int i = 1; i <= 19; i++) {'.")
        corrected_code = correct_syntactic(corrected_code)

    if not re.search(r'\{\s*\n\s*System\.out\.println\s*\(\s*".*"\s*\)\s*;\s*\n\s*\}', code):
        errors.append("Error en el cuerpo del bucle 'for'. Asegúrate de usar 'System.out.println()' correctamente y de que las llaves estén bien colocadas.")
        corrected_code = correct_syntactic(corrected_code)

    if not errors:
        return "Sintaxis correcta", corrected_code
    else:
        return " ".join(errors), corrected_code

def analyze_semantic(code):
    errors = []
    if not re.search(r'\bSystem\.out\.println\s*\(\s*".*"\s*\)\s*;', code):
        errors.append("Error semántico en System.out.println. Asegúrate de usar 'System.out.println()' correctamente con comillas dobles para las cadenas.")
        corrected_code = correct_semantic(code)
    else:
        corrected_code = code

    if not errors:
        return "Uso correcto de System.out.println", corrected_code
    else:
        return " ".join(errors), corrected_code

@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_results = []
    total_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    syntactic_result = ''
    semantic_result = ''
    corrected_code = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_results, total_results = analyze_lexical(code)
        syntactic_result, corrected_code = analyze_syntactic(code)
        semantic_result, corrected_code = analyze_semantic(corrected_code)
    return render_template_string(html_template, code=code, lexical=lexical_results, total=total_results, syntactic=syntactic_result, semantic=semantic_result, corrected_code=corrected_code)

if __name__ == '__main__':
    app.run(debug=True)
