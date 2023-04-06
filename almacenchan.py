#almacenchan.py
import os
import random
import sqlite3
#import discord
from dotenv import load_dotenv
from discord.ext import commands

# Configura el bot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

# Conecta la base de datos
conn = sqlite3.connect('warehouse.db')
c = conn.cursor()

# Crea una tabla para almacenar la información del almacen
c.execute('''CREATE TABLE IF NOT EXISTS warehouse
             (item TEXT, stock INTEGER, rareza TEXT CHECK(rareza IN ('A', 'B', 'N/A', '-')))''')

# Funcion comprobar campos
def validar_campos(item, stock, rareza="-"):
    if not item or not stock:
        raise ValueError("El nombre o stock del artículo no pueden estar vacíos.")
    return item, stock, rareza

# Función para agregar un artículo del almacen
@bot.command()
async def add_item(ctx, item, stock, rareza="-"):
    try:
        item, stock, rareza = validar_campos(item, stock, rareza)
        c.execute("INSERT INTO warehouse VALUES (?, ?, ?)", (item, stock, rareza))
        conn.commit()
        await ctx.send(f"{item} ha sido agregado al almacen.")
    except sqlite3.Error as error:
        print("Error al insertar los datos en la tabla de la base de datos", error)
        await ctx.send(f"Error al agregar {item} al almacen.")

# Función para quitar un artículo del almacen
# DELETE FROM `movies` WHERE `movie_id` = 18;
@bot.command()
async def delete_item(ctx, item, rareza="-"):
    try:
        if not item:
            raise ValueError("El nombre del artículo no pueden estar vacíos.")
        if not rareza:
            rareza = "-"    
        c.execute("DELETE FROM warehouse WHERE item=? AND rareza=?", (item, rareza))
        conn.commit()
        await ctx.send(f"{item} ha sido quitado del almacen.")
    except sqlite3.Error as error:
        print("Error al borrar los datos en la tabla de la base de datos", error)
        await ctx.send(f"Error al agregar {item} al almacen.")

# Función para mostrar los artículos en el stock
@bot.command()
async def show_items(ctx, categoria="*"):
    try:
        items = []
        if categoria == "*":
            c.execute("SELECT * FROM warehouse ORDER BY item")
        else:
            c.execute("SELECT * FROM warehouse WHERE item=?", (categoria,))
        rows = c.fetchall()
        for row in rows:
            items.append(f"{row[0]} -> Stock: {row[1]}    Rareza: {row[2]}")
        await ctx.send("\n".join(items))
    except sqlite3.Error as error:
        print("No hay articulos todavia", error)
        await ctx.send(f"Error al mostrar el almacen.")

# Función para agregar stock a un artículo
@bot.command()
async def add_stock(ctx, item, stock, rareza="-"):
    # Verifica si el artículo está en el stock
    try:
        item, stock, rareza = validar_campos(item, stock, rareza)
        c.execute("SELECT stock FROM warehouse WHERE item=? AND rareza=?", (item, rareza))
        result = c.fetchone()
        if result is None:
            await ctx.send("Ese artículo no está creado, crealo primero con add_item")
            return
    # Actualiza la base de datos con el stock adicional
        c.execute("UPDATE warehouse SET stock=stock+? WHERE item=? AND rareza=?", (stock, item, rareza))
        conn.commit()
        await ctx.send(f"{stock} unidades de {item} han sido agregadas al stock.")
    except sqlite3.Error as error:
        print("Error al agregar stock", error)
        await ctx.send(f"Error al agregar stock al {item} del almacen.")

# Función para retirar stock de un artículo
@bot.command()
async def comprar(ctx, item, stock, rareza="-"):
    try:
        item, stock, rareza = validar_campos(item, stock, rareza)
    # Verifica si el artículo está en el stock
        c.execute("SELECT stock FROM warehouse WHERE item=? AND rareza=?", (item, rareza))
        result = c.fetchone()
        if result is None:
            await ctx.send("Ese artículo no está en el stock.")
            return
    # Verifica si hay suficiente stock del artículo
        db_stock = int(stock)
        if result[0] < db_stock:
            await ctx.send("No hay suficiente stock de ese artículo.")
            return
    # Actualiza la base de datos con el stock retirado
        c.execute("UPDATE warehouse SET stock=stock-? WHERE item=? AND rareza=?", (stock, item, rareza))
        conn.commit()
        await ctx.send(f"{stock} unidad/es de {item} han sido retiradas del almacen.")
    except sqlite3.Error as error:
        print("Error al retirar stock", error)
        await ctx.send(f"Error al retirar stock al {item} del almacen.")

@bot.command()
async def ayuda(ctx):
        await ctx.send(f'!show_items comando para mostrar los objetos en venta, si especificas !show_items "Vivienda" te mostrara solo esa categoria')
        await ctx.send(f'!comprar comando para adquirir objetos, se pone de la siguiente manera !comprar Municion 5 A , primero el nombre, despues la cantidad y por ultimo si tiene, la rareza')

bot.run("TOKEN-AQUI")
