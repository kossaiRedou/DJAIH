from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import (
    Article, Skill, AboutSection, Contact, Service, SoftSkills,
    Employee, Project, Technology, Experience, Education,
    SoftSkills, Certification, Practice, Customer, HeroCarousel
)



#---------------------------------- soft skils
class SoftSkillsAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Afficher le champ 'name' dans la liste des objets
    search_fields = ('name',)  # Permettre la recherche par 'name'

# Enregistrer le modèle SoftSkills avec l'admin
admin.site.register(SoftSkills, SoftSkillsAdmin)



#==========================================
#               SERVICES
#===========================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "short_description", "created_at")
    search_fields = ("title", "short_description", "target_clients")
    list_filter = ("created_at",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Informations Générales", {"fields": ("title", "slug", "short_description", "detailed_description")}),
        ("Détails du Service", {"fields": ("benefits",  "target_clients")}),
        ("Médias", {"fields": ("image",)}),
        ("Appel à l'Action", {"fields": ("call_to_action",)}),
        ("Dates", {"fields": ("created_at",)}),
    )
    readonly_fields = ("created_at",)




#================================================================
#                    CONTACT
#=================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")  # Colonnes visibles
    search_fields = ("name", "email", "subject")  # Barre de recherche
    list_filter = ("created_at",)  # Filtres sur la date
    ordering = ("-created_at",)  # Tri par date décroissante






class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "published_date")
    list_filter = ("category", "published_date", "author")
    search_fields = ("title", "author", "category", "content")
    prepopulated_fields = {"slug": ("title",)}

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)

admin.site.register(Article, ArticleAdmin)





#====================================================
#            Portfolio
#====================================
class EducationInline(admin.TabularInline):  # Affichage en tableau
    model = Education
    extra = 0
    fields = ("degree", "specialty", "university", "start_date", "end_date", "city", "country", "description")


class ExperienceInline(admin.TabularInline):  # Affichage en tableau
    model = Experience
    extra = 0
    fields = ("position", "company", "start_date", "end_date", "is_current", "city", "technologies", "description")


class ProjectInline(admin.TabularInline):  # Affichage en tableau
    model = Project
    extra = 0
    fields = ("title", "slug", "description", "image", "technologies")




class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ("title", "platform", "link", "image", "skills")




# Mise à jour de l'admin Employee pour inclure les certifications
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "email", "phone", "location", "show_photo", "display_soft_skills")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "email", "position", "location", "softSkills__name")
    list_filter = ("position", "location", "softSkills")

    fieldsets = (
        ("👤 Informations Personnelles", {
            "fields": ("name", "slug", "email", "phone", "linkedin", "gitHub", "medium", "position", "photo", "cv", "location", "about", "softSkills"),
        }),
    )

    filter_horizontal = ("softSkills",)
    inlines = [EducationInline, ExperienceInline, ProjectInline, CertificationInline]  # Ajout des certifications ici !

    def show_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius:50%;" />')
        return "No Image"
    show_photo.short_description = "Photo"

    def display_soft_skills(self, obj):
        return ", ".join([skill.name for skill in obj.softSkills.all()])
    display_soft_skills.short_description = "Soft Skills"


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("position", "company", "start_date", "end_date", "employee", "city")
    search_fields = ("position", "company", "employee__name", "city")
    list_filter = ("company", "start_date", "is_current")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("specialty", "university", "start_date", "end_date", "employee", "city", "country")
    search_fields = ("specialty", "university", "employee__name", "city", "country")
    list_filter = ("university", "country", "start_date")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "employee", "show_image", "display_skills")
    search_fields = ("title", "platform", "employee__name", "skills__name")
    list_filter = ("platform",)
    filter_horizontal = ("skills",)

    def show_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:10%;" />')
        return "No Image"
    show_image.short_description = "Image"

    def display_skills(self, obj):
        return ", ".join([skill.name for skill in obj.skills.all()])
    display_skills.short_description = "Compétences acquises"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)




#==================================================
#          about Section
#===============================
@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "video_url")  # Affichage des champs clés
    search_fields = ("title", "year")  # Recherche rapide
    list_filter = ("year",)  # Filtres pour faciliter la recherche
    readonly_fields = ("preview_image",)  # Ajout d'un aperçu de l'image
    fieldsets = (
        ("Informations principales", {
            "fields": ("title", "year", "history_title", "history_text", "mission")
        }),
        ("Médias", {
            "fields": ("image", "preview_image", "video_url")
        }),
    )

    def preview_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" style="border-radius:10px;" />'
        return "Pas d'image"

    preview_image.allow_tags = True
    preview_image.short_description = "Aperçu de l'image"


# Nos pratiques
@admin.register(Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ("number", "title")
    ordering = ("number",)
    search_fields = ("title", "description")



# Nos Clients
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('nom', 'secteur', 'logo')  # Affichage dans la liste admin
    list_filter = ('secteur',)  # Filtrage par secteur
    search_fields = ('nom',)  # Barre de recherche par nom

admin.site.register(Customer, CustomerAdmin)


# Carousel Items
@admin.register(HeroCarousel)
class HeroCarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'image')
    list_editable = ('order',)
    search_fields = ('title',)





from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Article, Skill, AboutSection, Contact, Service, SoftSkills,
    Employee, Project, Technology, Experience, Education,
    SoftSkills, Certification, Practice, Customer, HeroCarousel
)




from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Article, Skill, AboutSection, Contact, Service, SoftSkills,
    Employee, Project, Technology, Experience, Education,
    SoftSkills, Certification, Practice, Customer, HeroCarousel
)

# -------------------------
# Admin pour les Projets
# -------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "employee", "date", "display_technologies", "demo_link", "depot_link", "image_preview")
    list_filter = ("date", "employee")
    search_fields = ("title", "employee__name", "technologies__name")
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        ("Informations Générales", {
            "fields": ("employee", "title", "slug", "description")
        }),
        ("Technologies utilisées", {
            "fields": ("technologies",)
        }),
        ("Médias", {
            "fields": ("image",)
        }),
        ("Liens", {
            "fields": ("demo", "depot")
        }),
        ("Autres", {
            "fields": ("date",)
        }),
    )
    filter_horizontal = ("technologies",)

    def display_technologies(self, obj):
        """ Affiche les technologies associées sous forme de liste """
        return ", ".join([tech.name for tech in obj.technologies.all()])

    display_technologies.short_description = "Technologies"

    def demo_link(self, obj):
        """ Affiche un lien cliquable vers la démo s'il existe """
        if obj.demo:
            return format_html('<a href="{}" target="_blank">Voir la démo</a>', obj.demo)
        return "Aucune"

    demo_link.short_description = "Lien Démo"

    def depot_link(self, obj):
        """ Affiche un lien cliquable vers le dépôt s'il existe """
        if obj.depot:
            return format_html('<a href="{}" target="_blank">Voir le dépôt</a>', obj.depot)
        return "Aucun"

    depot_link.short_description = "Lien Dépôt"

    def image_preview(self, obj):
        """ Affiche un aperçu de l'image si elle est disponible """
        if obj.image:
            return format_html('<img src="{}" width="75" height="75" style="border-radius: 5px;" />', obj.image.url)
        return "Pas d'image"

    image_preview.short_description = "Aperçu de l'image"
