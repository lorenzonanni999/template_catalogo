import asyncio
import tornado.web
from pymongo import AsyncMongoClient
from bson import ObjectId


UIds = "studente"
Pws = "ZPZfw5K6RWhOSani"

connection_string = (
    "mongodb+srv://" + UIds + ":" + Pws +
    "@cluster0.geflqhy.mongodb.net/?appName=Cluster0"
)

client = AsyncMongoClient(connection_string)
db = client["nanni_catalogo_db"]
catalogo_collection = db["catalogo"]


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("home2.html")


class CatalogoHandler(tornado.web.RequestHandler):
    async def get(self):
        prodotti = await catalogo_collection.find().to_list(length=None)
        self.render("catalog.html", products=prodotti)


class AggiungereHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html", nome=None, prezzo=None, categoria=None, disponibile=None)

    async def post(self):
        nome = self.get_body_argument("nome")
        prezzo = float(self.get_body_argument("prezzo"))
        categoria = self.get_body_argument("categoria")
        disponibile = self.get_body_argument("disponibile", default=None) == "on"

        nuovo_prodotto = {
            "name": nome,
            "price": prezzo,
            "category": categoria,
            "available": disponibile
        }

        await catalogo_collection.insert_one(nuovo_prodotto)

        prodotti = await catalogo_collection.find().to_list(length=None)
        self.render("catalog.html", products=prodotti)


class ModificaHandler(tornado.web.RequestHandler):
    async def post(self, id):
        oid = ObjectId(id)

        prodotto = await catalogo_collection.find_one({"_id": oid})

        if prodotto:
            new_value = not prodotto["available"]
            await catalogo_collection.update_one(
                {"_id": oid},
                {"$set": {"available": new_value}}
            )

        prodotti = await catalogo_collection.find().to_list(length=None)
        self.render("catalog.html", products=prodotti)


class EliminaHandler(tornado.web.RequestHandler):
    async def post(self, id):
        oid = ObjectId(id)

        await catalogo_collection.delete_one({"_id": oid})

        prodotti = await catalogo_collection.find().to_list(length=None)
        self.render("catalog.html", products=prodotti)


class CatalogoFiltraHandler(tornado.web.RequestHandler):
    async def post(self):
        categoria = self.get_body_argument("categoria")

        prodotti = await catalogo_collection.find({"category": categoria}).to_list(length=None)

        self.render("catalog.html", products=prodotti)

def make_app():
    return tornado.web.Application([
        (r"/", HomeHandler),
        (r"/catalogo", CatalogoHandler),
        (r"/aggiungere", AggiungereHandler),
        (r"/catalogo/modifica/([A-Za-z0-9]+)", ModificaHandler),
        (r"/catalogo/elimina/([A-Za-z0-9]+)", EliminaHandler),
        (r"/catalogo/filtra", CatalogoFiltraHandler)
    ], template_path="templates")


async def main(shutdown_event):
    app = make_app()
    app.listen(8891)
    print("Server attivo su http://localhost:8891")
    await shutdown_event.wait()


if __name__ == "__main__":
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()
