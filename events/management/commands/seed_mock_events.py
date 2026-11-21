from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from events.models import Event, EventCategory
from bookings.models import Booking, Ticket


class Command(BaseCommand):
    help = "Seed realistic campus events (both free and paid) to populate the platform"

    def handle(self, *args, **options):
        # 1. Ensure Organizers exist
        organizers_data = [
            {
                "email": "techclub@campus.ac.ke",
                "full_name": "Developer Student Club & Innovators",
                "phone_number": "254711223344",
                "role": "organizer",
            },
            {
                "email": "sports@campus.ac.ke",
                "full_name": "University Athletics & Sports Board",
                "phone_number": "254722334455",
                "role": "organizer",
            },
            {
                "email": "guild@campus.ac.ke",
                "full_name": "Student Association & Entertainment Committee",
                "phone_number": "254733445566",
                "role": "organizer",
            },
            {
                "email": "careers@campus.ac.ke",
                "full_name": "Career Development & Alumni Office",
                "phone_number": "254744556677",
                "role": "organizer",
            },
        ]

        organizers = {}
        # Also grab existing mutua organizer
        existing_mutua = User.objects.filter(email="mutua@africantechnologyforum.org").first()
        if existing_mutua:
            organizers["mutua"] = existing_mutua

        for data in organizers_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["email"],
                    "full_name": data["full_name"],
                    "phone_number": data["phone_number"],
                    "role": data["role"],
                    "is_approved": True,
                },
            )
            if created:
                user.set_password("CampusPass2026!")
                user.save()
            organizers[data["email"].split("@")[0]] = user

        # 2. Get categories
        cat_tech = EventCategory.objects.get(slug="technology-events")
        cat_acad = EventCategory.objects.get(slug="academic-seminars")
        cat_work = EventCategory.objects.get(slug="workshops")
        cat_career = EventCategory.objects.get(slug="career-events")
        cat_sports = EventCategory.objects.get(slug="sports")
        cat_ent = EventCategory.objects.get(slug="entertainment")
        cat_assoc = EventCategory.objects.get(slug="student-association-events")
        cat_comp = EventCategory.objects.get(slug="competitions")

        today = timezone.now().date()
        now = timezone.now()

        # 3. List of realistic mock events
        mock_events = [
            {
                "title": "East Africa University Hackathon 2026",
                "category": cat_comp,
                "organizer": organizers.get("techclub") or organizers.get("mutua"),
                "venue": "Science & Computing Complex, Lab 4 & 5",
                "event_date": today + timedelta(days=5),
                "start_time": time(8, 30),
                "end_time": time(19, 0),
                "ticket_price": 0,
                "maximum_tickets": 250,
                "registration_deadline": now + timedelta(days=4),
                "description": (
                    "Join over 200 student developers, designers, and innovators from across East Africa "
                    "for a 24-hour sprint. Solve real challenges across fintech, agri-tech, healthcare, and education.\n\n"
                    "• Grand Prize: KES 150,000 + Cloud Credits\n"
                    "• Free meals, mentor sessions, and tech swag bags for all accepted participants.\n"
                    "• Open to all undergraduate and postgraduate students."
                ),
            },
            {
                "title": "Annual Campus Cultural Festival & Gala Night",
                "category": cat_ent,
                "organizer": organizers.get("guild"),
                "venue": "Graduation Square Pavilion",
                "event_date": today + timedelta(days=12),
                "start_time": time(18, 0),
                "end_time": time(23, 30),
                "ticket_price": 350.00,
                "maximum_tickets": 600,
                "registration_deadline": now + timedelta(days=11),
                "description": (
                    "The biggest student entertainment spectacle of the semester! Experience live musical performances, "
                    "traditional cultural dances, fashion showcases, spoken word, and guest DJ sets.\n\n"
                    "Food trucks and campus club stalls will be open throughout the night. Entry strictly by digital ticket QR pass."
                ),
            },
            {
                "title": "AI in Finance & Algorithmic Trading Masterclass",
                "category": cat_work,
                "organizer": organizers.get("mutua") or organizers.get("techclub"),
                "venue": "School of Business, Executive Lecture Hall 2",
                "event_date": today + timedelta(days=7),
                "start_time": time(14, 0),
                "end_time": time(17, 30),
                "ticket_price": 500.00,
                "maximum_tickets": 100,
                "registration_deadline": now + timedelta(days=6),
                "description": (
                    "A hands-on intensive workshop breaking down how machine learning and quantitative models "
                    "are transforming modern African and global financial markets.\n\n"
                    "Topics covered:\n"
                    "1. Time-series forecasting with Python & PyTorch\n"
                    "2. Sentiment analysis on financial news & social sentiment\n"
                    "3. Risk management & portfolio optimization\n\n"
                    "Includes interactive Google Colab notebooks and certificate of attendance."
                ),
            },
            {
                "title": "Inter-University Rugby 7s Championship Finals",
                "category": cat_sports,
                "organizer": organizers.get("sports"),
                "venue": "University Main Sports Complex Grounds",
                "event_date": today + timedelta(days=9),
                "start_time": time(10, 0),
                "end_time": time(17, 0),
                "ticket_price": 200.00,
                "maximum_tickets": 800,
                "registration_deadline": now + timedelta(days=8),
                "description": (
                    "Witness high-voltage varsity rugby as top campus titans battle for the national inter-collegiate trophy! "
                    "Bring your college colors and cheer our home varsity team.\n\n"
                    "Cheerleading displays, half-time entertainment, and refreshments will be available at student rates."
                ),
            },
            {
                "title": "Tech Career Fair & Senior Executive Networking Mixer",
                "category": cat_career,
                "organizer": organizers.get("careers"),
                "venue": "University Great Hall, Level 1",
                "event_date": today + timedelta(days=15),
                "start_time": time(9, 0),
                "end_time": time(16, 0),
                "ticket_price": 0,
                "maximum_tickets": 400,
                "registration_deadline": now + timedelta(days=14),
                "description": (
                    "Connect directly with hiring managers, software leads, and recruiters from over 30 leading companies "
                    "including Safaricom, Microsoft ADC, Google, Equity Bank, and fast-growing regional startups.\n\n"
                    "Bring updated copies of your resume for on-the-spot interviews and free professional LinkedIn headshots."
                ),
            },
            {
                "title": "Full-Stack Web Development with Django & React Bootcamp",
                "category": cat_work,
                "organizer": organizers.get("techclub"),
                "venue": "ICT Innovation Centre, Room B12",
                "event_date": today + timedelta(days=18),
                "start_time": time(10, 0),
                "end_time": time(15, 0),
                "ticket_price": 450.00,
                "maximum_tickets": 75,
                "registration_deadline": now + timedelta(days=17),
                "description": (
                    "Take your programming skills from basics to production. Build and deploy a real-time full-stack "
                    "application using modern Django REST Framework and React.\n\n"
                    "Requirements: Basic knowledge of Python or JavaScript. Bring your laptop."
                ),
            },
            {
                "title": "Campus Chess Tournament & Blitz Challenge",
                "category": cat_comp,
                "organizer": organizers.get("sports"),
                "venue": "Student Union Games Room",
                "event_date": today + timedelta(days=10),
                "start_time": time(11, 0),
                "end_time": time(16, 30),
                "ticket_price": 100.00,
                "maximum_tickets": 64,
                "registration_deadline": now + timedelta(days=9),
                "description": (
                    "7-round Swiss system tournament open to all campus chess enthusiasts. FIDE rated arbiters "
                    "will oversee the boards. Trophies and cash prizes for top 3 positions."
                ),
            },
            {
                "title": "Climate Action & Renewable Energy Campus Summit",
                "category": cat_acad,
                "organizer": organizers.get("careers"),
                "venue": "Environmental Sciences Auditorium",
                "event_date": today + timedelta(days=21),
                "start_time": time(9, 30),
                "end_time": time(13, 30),
                "ticket_price": 0,
                "maximum_tickets": 300,
                "registration_deadline": now + timedelta(days=20),
                "description": (
                    "Keynote presentations and panel discussions from leading sustainability researchers, "
                    "solar energy engineers, and policy experts on driving net-zero transitions across African campuses."
                ),
            },
            {
                "title": "Stand-up Comedy & Acoustic Campus Night",
                "category": cat_ent,
                "organizer": organizers.get("guild"),
                "venue": "Taifa Hall Amphitheater",
                "event_date": today + timedelta(days=14),
                "start_time": time(19, 0),
                "end_time": time(22, 0),
                "ticket_price": 250.00,
                "maximum_tickets": 350,
                "registration_deadline": now + timedelta(days=13),
                "description": (
                    "Unwind before mid-semester exams with a side-splitting night of stand-up comedy featuring top "
                    "campus comedians, guest headliners, and relaxing acoustic performances."
                ),
            },
            {
                "title": "Cloud Architecture & DevOps with AWS & GCP",
                "category": cat_tech,
                "organizer": organizers.get("mutua") or organizers.get("techclub"),
                "venue": "Engineering Lab 2, 3rd Floor",
                "event_date": today + timedelta(days=25),
                "start_time": time(13, 0),
                "end_time": time(16, 30),
                "ticket_price": 600.00,
                "maximum_tickets": 80,
                "registration_deadline": now + timedelta(days=24),
                "description": (
                    "Learn containerization with Docker, Kubernetes orchestration, CI/CD pipelines, and cloud infra provisioning. "
                    "Hands-on architectural labs to help prepare for industry certifications."
                ),
            },
            {
                "title": "Annual Inter-Faculty Football Derby: Engineering vs Medicine",
                "category": cat_sports,
                "organizer": organizers.get("sports"),
                "venue": "University Stadium Pitch 1",
                "event_date": today + timedelta(days=8),
                "start_time": time(15, 30),
                "end_time": time(18, 0),
                "ticket_price": 150.00,
                "maximum_tickets": 1000,
                "registration_deadline": now + timedelta(days=8),
                "description": (
                    "The fiercest rivalry on campus takes center stage! Faculty of Engineering takes on Faculty of Medicine "
                    "in the knockout derby. Ticket holders get reserved bleacher seating and a match-day programme."
                ),
            },
            {
                "title": "Student Leadership, Ethics & Public Speaking Summit",
                "category": cat_assoc,
                "organizer": organizers.get("guild"),
                "venue": "Senate Conference Hall",
                "event_date": today + timedelta(days=28),
                "start_time": time(9, 0),
                "end_time": time(14, 0),
                "ticket_price": 0,
                "maximum_tickets": 150,
                "registration_deadline": now + timedelta(days=27),
                "description": (
                    "Designed for aspiring student union leaders, club executives, and class representatives. "
                    "Master negotiation, crisis communication, and ethical leadership in modern governance."
                ),
            },
        ]

        created_count = 0
        for data in mock_events:
            event, created = Event.objects.get_or_create(
                title=data["title"],
                defaults={
                    "category": data["category"],
                    "organizer": data["organizer"],
                    "venue": data["venue"],
                    "event_date": data["event_date"],
                    "start_time": data["start_time"],
                    "end_time": data["end_time"],
                    "ticket_price": data["ticket_price"],
                    "maximum_tickets": data["maximum_tickets"],
                    "registration_deadline": data["registration_deadline"],
                    "description": data["description"],
                    "publication_status": Event.PublicationStatus.PUBLISHED,
                    "is_approved": True,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} events! Total events: {Event.objects.count()}"))
