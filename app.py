import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine, text
import pandas as pd

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Conexión a la base de datos PostgreSQL en Azure utilizando SQLAlchemy
engine = create_engine('postgresql://DanielM:Promaster13031@quierollorar.postgres.database.azure.com:5432/DBfoundation')

# Función para cargar los datos desde la base de datos
def load_data():
    query = "SELECT * FROM inventario"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df

# Función para actualizar la base de datos
def update_db(data):
    with engine.connect() as conn:
        trans = conn.begin()  # Iniciar una transacción
        try:
            for row in data:
                sql = text("""
                UPDATE inventario
                SET nombre = :nombre, cantidad = :cantidad
                WHERE cajon = :cajon
                """)
                conn.execute(sql, {'nombre': row['nombre'], 'cantidad': row['cantidad'], 'cajon': row['cajon']})
            trans.commit()  # Confirmar la transacción
        except Exception as e:
            trans.rollback()  # Revertir la transacción en caso de error
            print(f"Error al actualizar la base de datos: {e}")

# Diseño de la aplicación
app.layout = html.Div([
    html.H1("Bienvenido a tu inventario :D"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i, "editable": True} for i in load_data().columns],
        data=load_data().to_dict('records'),
        editable=True,
        row_deletable=True,
        row_selectable='multi'
    ),
    html.Button('Guardar Cambios', id='save-button', n_clicks=0),
    html.Div(id='output'),
    dcc.Interval(
        id='interval-component',
        interval=60000,  # en milisegundos
        n_intervals=0
    )
])

# Callback para cargar los datos cada vez que el intervalo de actualización se dispara
@app.callback(
    Output('table', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_table_data(n_intervals):
    return load_data().to_dict('records')

# Callback para guardar los cambios en la base de datos
@app.callback(
    Output('output', 'children'),
    Input('save-button', 'n_clicks'),
    State('table', 'data')
)
def save_changes(n_clicks, rows):
    if n_clicks > 0:
        update_db(rows)
        return 'Datos actualizados en la base de datos'
    return ''

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)  # Aquí puedes especificar el puerto
