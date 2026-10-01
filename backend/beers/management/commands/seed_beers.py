from django.core.management.base import BaseCommand
from beers.models import Brand, Beer


BRANDS = [
    {
        'name': 'Heineken',
        'country': 'Paises Bajos',
        'founded_year': 1864,
        'description': 'Cerveceria neerlandesa, una de las marcas de cerveza mas vendidas del mundo.',
    },
    {
        'name': 'Guinness',
        'country': 'Irlanda',
        'founded_year': 1759,
        'description': 'Cerveceria irlandesa famosa por su stout negro de tradicion ceramica.',
    },
    {
        'name': 'Corona',
        'country': 'Mexico',
        'founded_year': 1925,
        'description': 'Grupo brewerero mexicano, lider mundial en exportaciones de cerveza.',
    },
    {
        'name': 'Modelo',
        'country': 'Mexico',
        'founded_year': 1925,
        'description': 'Cerveza pilsner mexicana, una de las marcas mas vendidas del pais.',
    },
    {
        'name': 'Craft Brew Co',
        'country': 'Estados Unidos',
        'founded_year': 2010,
        'description': 'Cerveza artesanal ficticia para demostrar el CRUD completo.',
    },
]

BEERS = [
    {'brand': 'Heineken', 'name': 'Heineken Original', 'beer_type': 'lager', 'alcohol_content': '5.00', 'ibu': 20, 'description': 'Lager premium con sabor equilibrado y final limpio.'},
    {'brand': 'Heineken', 'name': 'Heineken Silver', 'beer_type': 'lager', 'alcohol_content': '4.00', 'ibu': 18, 'description': 'Version mas ligera y moderna, menor cuerpo.'},
    {'brand': 'Guinness', 'name': 'Guinness Draught', 'beer_type': 'stout', 'alcohol_content': '4.20', 'ibu': 45, 'description': 'Stout cremoso con notas de cafe y chocolate.'},
    {'brand': 'Guinness', 'name': 'Guinness Extra Stout', 'beer_type': 'stout', 'alcohol_content': '5.60', 'ibu': 55, 'description': 'Version mas intensa y potente de la receta original.'},
    {'brand': 'Corona', 'name': 'Corona Extra', 'beer_type': 'lager', 'alcohol_content': '4.60', 'ibu': 22, 'description': 'Pilsner mexicana con toque de lima y sal.'},
    {'brand': 'Corona', 'name': 'Corona Premier', 'beer_type': 'lager', 'alcohol_content': '4.30', 'ibu': 21, 'description': 'Edicion premium con mayor cuerpo.'},
    {'brand': 'Modelo', 'name': 'Modelo Especial', 'beer_type': 'lager', 'alcohol_content': '4.40', 'ibu': 18, 'description': 'Pilsner mexicana iconica y perfecta para acompanar la comida.'},
    {'brand': 'Modelo', 'name': 'Modelo Negra', 'beer_type': 'porter', 'alcohol_content': '5.40', 'ibu': 30, 'description': 'Cerveza oscura porter con sabor robusto.'},
    {'brand': 'Craft Brew Co', 'name': 'Hoppy IPA', 'beer_type': 'ipa', 'alcohol_content': '6.50', 'ibu': 65, 'description': 'IPA artesanal con alto amargor y aromas citricos.'},
    {'brand': 'Craft Brew Co', 'name': 'Golden Ale', 'beer_type': 'ale', 'alcohol_content': '5.20', 'ibu': 25, 'description': 'Golden ale artesanal, dorada y suave.'},
    {'brand': 'Craft Brew Co', 'name': 'Wheat Sunrise', 'beer_type': 'wheat', 'alcohol_content': '4.80', 'ibu': 15, 'description': 'Cerveza de trigo con aroma citrico refrescante.'},
    {'brand': 'Craft Brew Co', 'name': 'Wild Sour', 'beer_type': 'sour', 'alcohol_content': '4.50', 'ibu': 10, 'description': 'Sour berliner-style, de acidez brillante.'},
]


class Command(BaseCommand):
    help = 'Carga datos de ejemplo de marcas y cervezas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--empty',
            action='store_true',
            help='Borra los datos existentes antes de cargar',
        )

    def handle(self, *args, **options):
        if Brand.objects.exists():
            if not options['empty']:
                self.stdout.write(self.style.WARNING(
                    'La base de datos ya tiene datos. Usa --empty para regenerarlos.'
                ))
                return
            Beer.objects.all().delete()
            Brand.objects.all().delete()
            self.stdout.write('Datos existentes eliminados.')

        brands_map = {}
        for b in BRANDS:
            brand, created = Brand.objects.get_or_create(
                name=b['name'],
                defaults={
                    'country': b['country'],
                    'founded_year': b['founded_year'],
                    'description': b['description'],
                },
            )
            brands_map[b['name']] = brand
            verb = 'creada' if created else 'ya existia'
            self.stdout.write(f"Marca '{brand.name}' {verb}")

        for b in BEERS:
            beer, created = Beer.objects.get_or_create(
                name=b['name'],
                brand=brands_map[b['brand']],
                defaults={
                    'beer_type': b['beer_type'],
                    'alcohol_content': b['alcohol_content'],
                    'ibu': b['ibu'],
                    'description': b['description'],
                },
            )
            verb = 'creada' if created else 'ya existia'
            self.stdout.write(f"Cerveza '{beer.name}' {verb}")

        self.stdout.write(self.style.SUCCESS(
            f'\nListo: {Brand.objects.count()} marcas y {Beer.objects.count()} cervezas.'
        ))
