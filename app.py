from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "demo_secret_key"

# 连接 Azure SQL 数据库
AZURE_SQL_URL = os.getenv("AZURE_SQL_URL", "mssql+pyodbc://sqladmin:Planning456!@sap-sqlserver.database.windows.net:1433/sapdb?driver=ODBC+Driver+17+for+SQL+Server")
engine = create_engine(AZURE_SQL_URL, pool_pre_ping=True)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        session["user"] = username
        if username.lower() == "admin":
            return redirect(url_for("setting"))
        else:
            return redirect(url_for("view"))
    return render_template("login.html")

@app.route("/setting")
def setting():
    if session.get("user", "").lower() != "admin":
        return redirect(url_for("view"))
    inspector = engine.inspect(engine)
    tables = inspector.get_table_names()
    return render_template("setting.html", user=session["user"], tables=tables)

@app.route("/view", methods=["GET", "POST"])
def view():
    user = session.get("user", "")
    selected_table = request.form.get("table") if request.method == "POST" else None
    df = pd.DataFrame()
    if selected_table:
        try:
            df = pd.read_sql(f"SELECT TOP 100 * FROM [{selected_table}]", con=engine)
        except Exception as e:
            df = pd.DataFrame({"error": [str(e)]})
    return render_template("view.html", user=user, table=selected_table, data=df.to_html(classes='table table-bordered table-striped', index=False, escape=False))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
