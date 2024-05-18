import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from sqlalchemy import create_engine, text
import pandas as pd

# Conexión a la base de datos PostgreSQL utilizando SQLAlchemy
engine = create_engine('postgresql://postgres:htYZzYoTPdNSLhnIdCcaJsdWqauDmNTF@viaduct.proxy.rlwy.net:42002/railway')

# Consulta SQL para obtener los datos de la tabla
query = "SELECT * FROM inventario"

# Obtener datos de la tabla utilizando pandas y SQLAlchemy
df = pd.read_sql(query, engine)

# Crear la aplicación Dash
app = dash.Dash(__name__)
server = app.server  # Exponer la instancia de Flask subyacente

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Diseño de la aplicación
app.layout = html.Div([
    html.H1("Tabla de la Base de Datos"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i, "editable": True} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        row_deletable=True,
        row_selectable='multi'
    ),
    html.Button('Guardar Cambios', id='save-button', n_clicks=0),
    html.Div(id='output')
])

# Función para actualizar la base de datos
def update_db(data):
    conn = engine.connect()
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
    finally:
        conn.close()

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
    app.run_server(debug=True)
