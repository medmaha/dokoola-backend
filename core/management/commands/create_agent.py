import sys
from typing import Any

from django.core.management import BaseCommand
from django.db import transaction

from clients.serializer import Client, ClientCreateSerializer, Company
from users.serializer import User, UserWriteSerializer


class Command(BaseCommand):

    def __get_user(self, data, password):

        serializer = UserWriteSerializer(data=data)
        if not serializer.is_valid():
            raise ValueError("Error: Agent-User already exists")

        user = User(**serializer.validated_data)
        user.is_client = True
        user.set_password(password)
        user.save()
        return user

    def handle(self, *args: Any, **options: Any) -> str | None:

        password = "%10medmahaDK"
        personal_data = {
            "phone": "",
            "gender": "other",
            "last_name": "Agent",
            "first_name": "Dokoola",
            "username": "dokoola-agent",
            "email": "inmaha33@gmail.com",
            "address": "Serrekunda, KMC",
            "avatar": "/img/logos/dokoola-avatar.png",
        }

        client = None

        try:
            user = self.__get_user(personal_data, password=password)
            if not user.check_password(password):
                self.stdout(self.style.ERROR("Agent-User password not hashed"))
                return sys.exit(1)

        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
            user = User.objects.get(email=personal_data["email"])
            client = Client.objects.only("pk").filter(user=user).first()

        with transaction.atomic():

            country_info = {
                "code": "GM",
                "name": "Gambia",
                "phone": "+220",
                "region": "Western Africa",
                "currency": "GMD",
            }

            company_data = {
                "name": "Dokoola Agent",
                "slug": "dokoola-agent",
                "logo_url": "/img/logos/dokoola.png",
                "website": "https://www.dokoola.com",
                "industry": "Job Marketplace & Freelancing",
                "date_established": "2025-01-01",
                "id": "279082e6-2387-4ea1-a92a-47453f295e6f",
                "description": "Dokoola is a digital job marketplace connecting professionals with job opportunities, including freelance, full-time, part-time, contract, and internship roles. The platform simplifies hiring by bringing jobs from various sources and enabling direct engagement between employers and skilled professionals.",
            }

            client_data = {
                "is_agent": True,
                "public_id": "cl_067a7796b41e71988",
                "id": "279082e6-2387-4ea1-a92a-47453f295e6f",
                "about": "Dokoola Agent is an official job-sourcing entity within the Dokoola marketplace, responsible for bringing external job opportunities onto the platform. It ensures a steady flow of freelance, full-time, part-time, contract, and internship roles from various sources, making job discovery easier for professionals.",
            }

            serializer = ClientCreateSerializer(
                instance=client,
                data={
                    **client_data,
                    **country_info,
                    **personal_data,
                },
            )

            if not serializer.is_valid():
                self.stdout.write(self.style.ERROR(str(serializer.errors)))
                return sys.exit(1)

            company, _ = Company.objects.get_or_create(
                name=company_data.pop("name"), defaults=company_data
            )
            client = serializer.save(user=user, company=company, **client_data)
