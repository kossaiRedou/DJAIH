from django.db import models
from django.utils.text import slugify
import itertools
from django.db import models
from django.utils.safestring import mark_safe
import markdown
import itertools
from django.utils.timezone import now
import markdown





class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True)  # Date automatique

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"





#===========================================
#                  Article
#==============================
class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name="Titre")
    slug = models.SlugField(unique=False, blank=True, verbose_name="Slug") # a revoir
    author = models.CharField(max_length=100, verbose_name="Auteur")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    content = models.TextField(verbose_name="Contenu (Markdown)")  # Markdown pour le texte et le code
    image = models.ImageField(upload_to="articles/", verbose_name="Image", null=True, blank=True)
    published_date = models.DateField(auto_now_add=True, verbose_name="Date de publication")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Générer un slug à partir du titre
        super().save(*args, **kwargs)


    def render_markdown(self):
        """Convertit le Markdown en HTML avec support des formules mathématiques."""
        return mark_safe(markdown.markdown(
            self.content,
            extensions=[
                "fenced_code",
                "codehilite",
                "pymdownx.arithmatex"  # Support pour LaTeX
            ]
        ))


    def __str__(self):
        return f"{self.title} - {self.author}"







#======================================================================
#                        Portfolio
#====================================================

class SoftSkills(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    linkedin = models.URLField(blank=True, null=True)
    gitHub = models.URLField(blank=True, null=True)
    medium = models.URLField(blank=True, null=True)

    position = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=100)

    about = models.TextField(max_length=1200, null=True)
    softSkills = models.ManyToManyField(SoftSkills, related_name='employees')
    cv = models.FileField(upload_to='KOTO/media/cvs', blank=True, null=True)  # Ajout du champ CV

    def save(self, *args, **kwargs):
        # Vérifier si l'objet est nouveau ou si le nom a changé
        if not self.pk or not self.slug.startswith(slugify(self.name)):
            base_slug = slugify(self.name, allow_unicode=True).replace("-", "_")
            slug = base_slug

            for i in itertools.count(1):
                if not Employee.objects.filter(slug=slug).exclude(id=self.id).exists():
                    break
                slug = f"{base_slug}_{i}"

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name





class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name





class Project(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=False, blank=True, null=True) # a revoir

    date = models.DateField(default=now)
    description = models.TextField()

    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    technologies = models.ManyToManyField(Technology, related_name='projects')

    demo = models.URLField(blank=True, null=True)
    depot = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            for i in itertools.count(1):
                if not Project.objects.filter(slug=slug).exists():
                    break
                slug = f"{base_slug}_{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def render_markdown(self):
        """Convertit le Markdown en HTML avec coloration syntaxique."""
        return mark_safe(markdown.markdown(
            self.description,
            extensions=["fenced_code", "codehilite"]  # Active les blocs de code
        ))

    def __str__(self):
        return f"{self.title} - {self.employee.name}"


class Experience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='experiences')
    position = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(max_length=1200)
    technologies = models.ManyToManyField(Technology, related_name='experiences')
    city = models.CharField(max_length=100)

    class Meta:
        ordering = ['-start_date']


    def save(self, *args, **kwargs):
        # Enregistrer d'abord l'expérience
        super().save(*args, **kwargs)

        # Si cette expérience est marquée comme étant "actuelle"
        if self.is_current:
            employee = self.employee
            # Mise à jour de la position et de la location de l'employé
            employee.position = self.position
            employee.location = self.city
            # Sauvegarde de l'employé avec les nouvelles informations
            employee.save(update_fields=['position', 'location'])



    def __str__(self):
        end_date_display = self.end_date.strftime("%Y") if self.end_date else "En cours"
        return f"{self.position} at {self.company} ({end_date_display})"




class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Certification(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=150)  # Titre de la certification
    platform = models.CharField(max_length=100)  # Plateforme délivrant la certif (Udemy, Coursera...)
    link = models.URLField(blank=True, null=True)  # Lien vers la certification
    image = models.ImageField(upload_to='certifications/', blank=True, null=True)  # Image de la certification
    skills = models.ManyToManyField(Skill, related_name='certifications')  # Compétences acquises
    date = models.DateField(default=now)

    class Meta:
        ordering = ['-date']  # Tri par date décroissante (du plus récent au plus ancien)

    def __str__(self):
        return f"{self.title} - {self.platform}"














class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=100, blank=True, null=True)
    specialty = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(max_length=500)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        end_date_display = self.end_date.strftime("%Y") if self.end_date else "En cours"
        return f"{self.specialty} - {self.university} ({end_date_display})"





#================================================
#            Section About
#===================================
class AboutSection(models.Model):
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=4)
    history_title = models.CharField(max_length=255)
    history_text = models.TextField()
    mission = models.TextField(default=None)  # <== Assure-toi que ce champ existe bien !
    image = models.ImageField(upload_to="about_images/", null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)



    def __str__(self):
        return self.title



#========================================================
#                   SERVICES
#========================================

class Service(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Titre du service"
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        #editable=False
    )
    short_description = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Description courte",
        help_text="Une phrase percutante qui résume le service."
    )
    detailed_description = models.TextField(
        null=True,
        verbose_name="Description complète",
        help_text="Explique en quoi ce service est utile et ses avantages."
    )
    benefits = models.TextField(
        null=True,
        verbose_name="Avantages clés",
        help_text="Liste des bénéfices concrets, séparés par des virgules."
    )
    target_clients = models.CharField(
        max_length=255,
        null=True,
        verbose_name="Public cible",
        help_text="Ex: Startups, PME, Grandes entreprises, Freelancers..."
    )
    image = models.ImageField(
        upload_to="services/",
        blank=True,
        null=False,
        verbose_name="Image illustrant le service"
    )
    call_to_action = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Texte d'appel à l'action",
        help_text="Ex: Contactez-nous pour une consultation gratuite"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['created_at']  # Optionnel, pour trier les services par date de création

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Service.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)



class Testimonial(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom du client")
    feedback = models.TextField(verbose_name="Témoignage")
    company = models.CharField(max_length=255, null=True, blank=True, verbose_name="Entreprise (optionnel)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.company if self.company else 'Indépendant'}"









# Nos pratiques:
class Practice(models.Model):
    number = models.PositiveIntegerField(verbose_name="Numéro", unique=True)  # Empêche les doublons
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")

    class Meta:
        ordering = ['number']
        verbose_name = "Pratique"
        verbose_name_plural = "Nos Pratiques"

    def formatted_number(self):
        """Retourne le numéro formaté avec deux chiffres (ex: 02, 03, 10)"""
        return f"{self.number:02d}"

    def __str__(self):
        """Affichage propre dans Django Admin et autres vues"""
        return f"{self.formatted_number()}. {self.title}"



#========================================================
#                   Customers
#========================================

class Customer(models.Model):
    SECTEURS_CHOICES = [
        ('tech', 'Technologie'),
        ('finance', 'Finance'),
        ('sante', 'Santé'),
        ('ecommerce', 'E-commerce'),
        ('industrie', 'Industrie'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='clients/')
    secteur = models.CharField(max_length=50, choices=SECTEURS_CHOICES, default='autre')

    def __str__(self):
        return f"{self.nom} - {self.get_secteur_display()}"




#=========================================
# Carousel items
#=====================
class HeroCarousel(models.Model):
    image = models.ImageField(upload_to='hero-carousel/')
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.IntegerField(default=0)  # Permet de trier les éléments du carrousel

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']  # Trier les éléments du carrousel par ordre croissant
