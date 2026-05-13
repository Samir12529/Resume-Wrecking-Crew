import chromadb

# Initialize a local database folder named 'resume_vector_db'
db_client = chromadb.PersistentClient(path="./resume_vector_db")

# Create a collection called perfect_resume_bullets
collection = db_client.get_or_create_collection(name="perfect_resume_bullets")

# Synthetic resume data (should be much more)
synthetic_data = [
    "Tech/Software: Engineered a distributed microservices architecture using Python and Docker, reducing system latency by 40% and supporting 10,000+ concurrent users.",
    "Tech/Software: Optimized legacy SQL database queries, decreasing data retrieval time by 60% and saving $5,000 annually in cloud computing costs.",
    "Finance: Managed a $5M portfolio, utilizing advanced Excel financial modeling and Python data analysis to identify market trends, resulting in a 12% YoY return.",
    "Marketing: Directed a cross-channel digital marketing campaign with a $50,000 budget, achieving a 300% ROI and acquiring 25,000 new active leads within Q3.",
    "Management: Led a cross-functional team of 15 engineers and designers using Agile methodologies, delivering the flagship product 2 weeks ahead of schedule and 10% under budget.",
    "Customer Success: Resolved escalated enterprise client issues, maintaining a 98% customer retention rate and generating $1.2M in contract renewals.",
    "Sales: Exceeded Q4 sales targets by 150%, closing $2.5M in enterprise software deals within a 6-month period by optimizing the outbound strategy.",
    "Design: Redesigned the core user onboarding flow, increasing user activation rate by 25% and reducing user drop-offs by 15% in the first week.",
    "Operations: Streamlined global supply chain logistics, reducing freight costs by 18% and decreasing average product delivery time by 2 days.",
    "Healthcare: Managed patient intake protocols across 3 regional clinics, increasing daily throughput by 20% while maintaining a 99% HIPAA compliance rate.",
    "Education: Developed and implemented a new STEM curriculum for 500+ students, resulting in a 35% improvement in standardized test scores year-over-year.",
    "Data Science: Built and deployed predictive machine learning models using Scikit-Learn, improving customer churn forecasting accuracy by 22%.",
    "HR: Overhauled the talent acquisition pipeline, reducing average time-to-hire from 45 to 28 days while increasing diversity hires by 30%.",
    "Tech/Software: Migrated monolithic on-premise infrastructure to AWS Cloud, achieving 99.99% uptime and scaling server capacity by 3x.",
    "Marketing: Orchestrated a re-branding initiative across 5 social platforms, growing organic follower count by 100,000 in under 6 months.",
    "Finance: Conducted comprehensive variance analysis on a $20M operating budget, identifying $1.5M in cost-saving opportunities across 4 departments.",
    "IT Support: Implemented an automated Zendesk ticketing system, decreasing average first-response time from 4 hours to just 15 minutes.",
    "Engineering: Designed and tested mechanical enclosures for consumer electronics using AutoCAD, reducing manufacturing defect rates by 12%.",
    "Product Management: Launched a new mobile app feature set, capturing 50,000 active users in the first week and driving a 10% increase in in-app purchases.",
    "Cybersecurity: Conducted weekly penetration testing and vulnerability assessments, remediating 50+ critical security flaws before the annual compliance audit."
]
ids = [f"bullet_{i}" for i in range(len(synthetic_data))]

collection.add(
    documents=synthetic_data,
    ids=ids
)
# Note that synthetic_data is raw text here. So where are the vectors?
# The answer is: ChromaDB automatically runs an embedding model in the background that turns this text into vectors.