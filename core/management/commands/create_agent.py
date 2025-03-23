import sys
from typing import Any

from django.core.management import BaseCommand
from django.db import transaction


class Command(BaseCommand):

    def __get_user(self, data, password, serializer):
        serializer = serializer(data=data)
        if not serializer.is_valid():
            raise ValueError("Error: User already exists")
        user = serializer.save(password=password, is_client=True)
        return user

    def handle(self, *args: Any, **options: Any) -> str | None:
        from clients.serializer import Client, ClientCreateSerializer, Company
        from users.serializer import User, UserWriteSerializer

        password = "%10medmahaDK"

        _personal_data = {
            "phone": "",
            "gender": "other",
            "last_name": "Agent",
            "first_name": "Dokoola",
            "username": "dokoola-agent",
            "email": "inmaha33@gmail.com",
            "address": "Serrekunda, KMC",
            "avatar": "/img/logos/dokoola-avatar.png",
        }

        try:
            with transaction.atomic():
                user = self.__get_user(
                    _personal_data, password=password, serializer=UserWriteSerializer
                )

                _country_info = {
                    "code": "GM",
                    "name": "Gambia",
                    "phone": "+220",
                    "region": "Western Africa",
                    "currency": "GMD",
                }

                _company_data = {
                    "name": "Dokoola Agent",
                    "slug": "dokoola-agent",
                    "logo_url": "/img/logos/dokoola.png",
                    "website": "https://www.dokoola.com",
                    "industry": "Job Marketplace & Freelancing",
                    "date_established": "2025-01-01",
                    "id": "279082e6-2387-4ea1-a92a-47453f295e6f",
                    "description": "Dokoola is a digital job marketplace connecting professionals with job opportunities, including freelance, full-time, part-time, contract, and internship roles. The platform simplifies hiring by bringing jobs from various sources and enabling direct engagement between employers and skilled professionals.",
                }

                _client_data = {
                    "is_agent": True,
                    "public_id": "cl_067a7796b41e71988",
                    "id": "279082e6-2387-4ea1-a92a-47453f295e6f",
                    "about": "Dokoola Agent is an official job-sourcing entity within the Dokoola marketplace, responsible for bringing external job opportunities onto the platform. It ensures a steady flow of freelance, full-time, part-time, contract, and internship roles from various sources, making job discovery easier for professionals.",
                }

                serializer = ClientCreateSerializer(
                    data={
                        **_client_data,
                        **_country_info,
                        **_personal_data,
                    }
                )

                if not serializer.is_valid():
                    self.stdout.write(serializer.errors)
                    return sys.exit(1)

                company = Company.objects.create(**_company_data)
                client = serializer.save(user=user, company=company, **_client_data)
                self.stdout.write("Dokoola Agent created successfully")

        except ValueError as e:
            self.stdout.write(str(e))
