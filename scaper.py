import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os


class HabrCareerScraper:
    def __init__(self):
        self.base_url = "https://career.habr.com/vacancies"
        self.scraper = cloudscraper.create_scraper()
        self.data = []
        self.seen_ids = set()

    def parse_page(self, keyword, page):
        params = {
            'q': keyword,
            'type': 'all',
            'page': page
        }

        try:
            response = self.scraper.get(self.base_url, params=params)
            if response.status_code != 200:

                return False

            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='vacancy-card')

            if not cards:
                return False

            for card in cards:
                link_elem = card.find('a', class_='vacancy-card__title-link')
                vac_id = link_elem['href'] if link_elem else None

                if vac_id and vac_id not in self.seen_ids:
                    self.seen_ids.add(vac_id)

                    title = link_elem.text.strip()
                    salary = card.find('div', class_='vacancy-card__salary')
                    company = card.find(
                        'div', class_='vacancy-card__company-title')
                    skills = card.find('div', class_='vacancy-card__skills')
                    date = card.find('time', class_='vacancy-card__date')

                    self.data.append({
                        'title': title,
                        'company': company.text.strip() if company else "Не указана",
                        'salary': salary.text.strip() if salary else "По договоренности",
                        'skills': skills.text.strip() if skills else "",
                        'date': date['datetime'] if date else "",
                        'link': f"https://career.habr.com{vac_id}"
                    })
            return True

        except Exception as e:

            return False

    def run(self, target_count=10000):
        keywords = [
            "Data Scientist", "Python", "Data Analyst", "Machine Learning",
            "Data Engineer", "Backend", "Frontend", "DevOps", "QA", "Java", "JavaScript",
            "C#", "C++", "Go", "Ruby", "PHP", "Scala", "Kotlin", "Swift", "Django", "Flask", "React", "Angular", "Vue", "AWS", "Azure", "GCP",
            "Docker", "Kubernetes", "SQL", "NoSQL", "Big Data", "Hadoop", "Spark", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "Deep Learning",
            "Data Visualization", "Business Intelligence", "ETL", "Airflow", "Kafka", "Redis", "MongoDB", "PostgreSQL", "MySQL", "IT Support", "System Administrator", "Network Engineer", "Cybersecurity", "Blockchain", "IoT", "AR/VR", "Game Development", "IT"
        ]

        for kw in keywords:
            if len(self.data) >= target_count:
                break

            for page in range(1, 101):
                if len(self.data) >= target_count:
                    break

                success = self.parse_page(kw, page)
                if not success:
                    break

                time.sleep(random.uniform(1.2, 2.5))

        return pd.DataFrame(self.data)


scraper = HabrCareerScraper()
df = scraper.run(target_count=5300)


home = os.path.expanduser("~")
downloads_path = os.path.join(home, "Downloads", "habr_vacancies_5300.csv")


df.to_csv(downloads_path, index=False, encoding='utf-8-sig')
