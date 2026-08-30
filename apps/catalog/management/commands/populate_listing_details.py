from decimal import Decimal
from django.core.management.base import BaseCommand
from apps.catalog.models import Listing


class Command(BaseCommand):
    help = "Заполняет новые поля (комнаты, мебель, ключевые места, координаты, описание) для всех объявлений"

    def handle(self, *args, **options):
        listings = Listing.all_objects.all()
        count = listings.count()
        self.stdout.write(f"Найдено {count} объявлений для обновления...")

        if count == 0:
            self.stdout.write(self.style.WARNING("В базе нет объявлений."))
            return

        updated_count = 0

        for l in listings:
            district_name = l.district.name.lower() if l.district else ""
            slug_lower = l.slug.lower()

            # 1. Ключевые места (landmarks)
            if not l.landmarks:
                if "асанбай" in district_name or "asanbay" in slug_lower:
                    l.landmarks = ["Парк Асанбай", "Гипермаркет Globus", "Школа Газпром"]
                elif "технопарк" in district_name or "technopark" in slug_lower:
                    l.landmarks = ["Школа 56", "Магистраль-Бакаева", "Клиника Эскулап"]
                elif "южн" in district_name or "yuzhn" in slug_lower:
                    l.landmarks = ["Парк Победы", "Магистраль", "ТРЦ Ала-Арча"]
                elif "центр" in district_name or "center" in slug_lower:
                    l.landmarks = ["Площадь Ала-Тоо", "ЦУМ Айчүрөк", "Парк Панфилова"]
                else:
                    l.landmarks = ["Школа 56", "Магистраль-Бакаева", "Клиника Эскулап"]

            # 2. Координаты (latitude, longitude)
            if not l.latitude or not l.longitude:
                if "асанбай" in district_name or "asanbay" in slug_lower:
                    l.latitude = Decimal("42.815200")
                    l.longitude = Decimal("74.623100")
                elif "технопарк" in district_name or "technopark" in slug_lower:
                    l.latitude = Decimal("42.825632")
                    l.longitude = Decimal("74.587321")
                elif "южн" in district_name or "yuzhn" in slug_lower:
                    l.latitude = Decimal("42.818900")
                    l.longitude = Decimal("74.605400")
                elif "центр" in district_name or "center" in slug_lower:
                    l.latitude = Decimal("42.874600")
                    l.longitude = Decimal("74.603700")
                else:
                    l.latitude = Decimal("42.825632")
                    l.longitude = Decimal("74.587321")

            # 3. Адрес
            if not l.address or l.address.strip() == "":
                if "асанбай" in district_name or "asanbay" in slug_lower:
                    l.address = "Бишкек, мкр. Асанбай, \nул. Аалы Токомбаева 21"
                elif "технопарк" in district_name or "technopark" in slug_lower:
                    l.address = "Бишкек, Октябрьский район, \nул.Бакаева 178/4"
                elif "южн" in district_name or "yuzhn" in slug_lower:
                    l.address = "Бишкек, \nул. Байтик Баатыра 180"
                else:
                    l.address = "Бишкек, Октябрьский район, \nул.Бакаева 178/4"

            # 4. Описание
            if not l.description or len(l.description.strip()) < 10 or "Сатурн" in l.description:
                if "асанбай" in district_name or "asanbay" in slug_lower:
                    l.description = "Роскошная квартира в ЖК Премиум класса. Дизайнерский ремонт, панорамные окна, вся мебель и техника остаются. Рядом парк, школы и супермаркеты."
                elif "технопарк" in district_name or "technopark" in slug_lower:
                    l.description = "Отличная квартира в районе Технопарка. Развитая инфраструктура, свежий евроремонт, новые трубы и проводка. Отличный вид из окон."
                elif "дом" in l.kind.lower() or "house" in slug_lower:
                    l.description = "Просторный дом в тихом престижном районе. Участок 6 соток, ландшафтный дизайн, навес на 3 авто, зона барбекю."
                else:
                    l.description = "Светлая и просторная квартира с панорамными окнами и видом на горы. Дизайнерский ремонт, качественные европейские материалы. В шаговой доступности школы, детские сады, парковые зоны и торговые центры."

            # 5. Мебель
            if not l.furniture:
                l.furniture = "Полностью"

            # 6. Варианты покупки
            l.has_direct_sale = True
            l.has_mortgage = True

            # 7. Квадратуры комнат
            total_sqm = float(l.area) if l.area else 92.0

            if not l.living_room_area:
                if "асанбай" in district_name or "asanbay" in slug_lower or total_sqm >= 110:
                    l.living_room_area = Decimal("42.0")
                    l.hall_area = Decimal("20.0")
                    l.kitchen_area = Decimal("18.0")
                    l.bedroom_area = Decimal("24.0")
                    l.bedroom_2_area = Decimal("16.0")
                    l.balcony_area = Decimal("8.0")
                    l.bathroom_area = Decimal("11.0")
                elif "технопарк" in district_name or "technopark" in slug_lower or (80 <= total_sqm < 110):
                    l.living_room_area = Decimal("35.0")
                    l.hall_area = Decimal("23.0")
                    l.kitchen_area = Decimal("17.0")
                    l.bedroom_area = Decimal("25.0")
                    l.bedroom_2_area = Decimal("15.0")
                    l.balcony_area = Decimal("7.0")
                    l.bathroom_area = Decimal("10.0")
                else:
                    l.living_room_area = Decimal(str(round(total_sqm * 0.35, 1)))
                    l.kitchen_area = Decimal(str(round(total_sqm * 0.18, 1)))
                    l.hall_area = Decimal(str(round(total_sqm * 0.15, 1)))
                    l.bedroom_area = Decimal(str(round(total_sqm * 0.22, 1)))
                    l.bedroom_2_area = Decimal(str(round(total_sqm * 0.14, 1))) if total_sqm > 55 else None
                    l.bathroom_area = Decimal(str(round(total_sqm * 0.08, 1)))
                    l.balcony_area = Decimal(str(round(total_sqm * 0.06, 1)))

            l.save()
            updated_count += 1
            self.stdout.write(f"Обновлено: [{l.slug}]")

        self.stdout.write(self.style.SUCCESS(f"Успешно обновлено {updated_count} объявлений!"))
