import math
import tkinter as tk
import time
from PIL import Image, ImageTk

class Bille:
    def __init__(self, canevas, numero, x, y, rayon, couleur):
        self.canevas = canevas
        self.numero = numero
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.id = self.dessiner()
        self.shadow_id, self.text_id = self.dessiner_nombre()
        self.vx = 0.0
        self.vy = 0.0
        self.trail_ids = []
        self.reflection_id = None
        self.dans_trou = False

    def dessiner(self):
        self.id = self.canevas.create_oval(
            self.x - self.rayon, self.y - self.rayon,
            self.x + self.rayon, self.y + self.rayon,
            fill=self.couleur, outline="black", width=1
        )
        return self.id

    def dessiner_nombre(self):
        shadow_id = self.canevas.create_text(
            self.x + 1, self.y + 1,
            text=str(self.numero),
            fill="black", font=("Arial", 12, "bold")
        )
        text_id = self.canevas.create_text(
            self.x, self.y,
            text=str(self.numero),
            fill="white", font=("Arial", 12, "bold")
        )
        return shadow_id, text_id

    def mettre_a_jour_position(self, x, y):
        for trail_id in self.trail_ids:
            self.canevas.delete(trail_id)
        self.trail_ids = []
        if abs(self.vx) > 2 or abs(self.vy) > 2:
            trail = self.canevas.create_oval(
                self.x - self.rayon//2, self.y - self.rayon//2,
                self.x + self.rayon//2, self.y + self.rayon//2,
                fill=self.couleur, outline="", width=0
            )
            self.trail_ids.append(trail)
            self.canevas.tag_lower(trail)
        self.x = x
        self.y = y
        self.canevas.coords(self.id, x - self.rayon, y - self.rayon, x + self.rayon, y + self.rayon)
        self.canevas.coords(self.text_id, x, y)
        self.canevas.coords(self.shadow_id, x + 1, y + 1)

class Canne:
    def __init__(self, canevas, bille, joueur_actuel):
        self.canevas = canevas
        self.bille = bille
        self.angle = 90
        self.puissance = 100
        self.proj_id = None
        self.id = None
        self.id_shadow = None
        self.poids = 0.5
        self.wtour = 0
        self.couleur = "red" if joueur_actuel == 1 else "orange"
        self.label_info = tk.Label(self.canevas, text='Hello', bg='#2C3E50', fg='white', font=("Arial", 14, "bold"),
                                    relief="solid", bd=0, highlightthickness=3, highlightbackground="#34495E", highlightcolor="#34495E")
        self.label_info.place(x=720, y=50, anchor="ne")

    def dessiner(self):
        if self.id:
            self.canevas.delete(self.id)
        if self.id_shadow:
            self.canevas.delete(self.id_shadow)
        if self.proj_id:
            self.canevas.delete(self.proj_id)
        dx = math.sin(math.radians(self.angle))
        dy = math.cos(math.radians(self.angle))
        longueur = 50 + self.puissance
        x2 = self.bille.x + dx * longueur
        y2 = self.bille.y - dy * longueur
        self.id_shadow = self.canevas.create_line(
            self.bille.x, self.bille.y, x2, y2,
            fill="#8B0000", width=6
        )
        self.id = self.canevas.create_line(
            self.bille.x, self.bille.y, x2, y2,
            fill=self.couleur, width=4
        )
        longueur_proj = max(self.canevas.winfo_width(), self.canevas.winfo_height())
        x_proj = self.bille.x - dx * longueur_proj
        y_proj = self.bille.y + dy * longueur_proj
        self.proj_id = self.canevas.create_line(
            self.bille.x, self.bille.y, x_proj, y_proj,
            fill="white", width=2, dash=(5, 2)
        )
        self.label_info.config(text=f'Puissance: {self.puissance}  |  Angle: {self.angle}°')

    def tourner_gauche(self):
        self.wtour += 0.5
        self.angle = (self.angle - self.wtour) % 360
        self.dessiner()

    def tourner_droite(self):
        self.wtour += 0.5
        self.angle = (self.angle + self.wtour) % 360
        self.dessiner()

    def raz(self):
        self.wtour = 0

    def ajuster_puissance(self, delta):
        self.puissance = min(120, max(0, self.puissance + delta))
        self.dessiner()

class JeuDeBillard:
    def __init__(self):
        self.racine = tk.Tk()
        self.racine.attributes('-fullscreen', True)
        self.largeur = self.racine.winfo_screenwidth()
        self.hauteur = self.racine.winfo_screenheight()
        self.marge = 100
        self.rayon_bille = 15
        self.billes = []
        self.trous = []
        self.billes_tombees = []
        self.position_precedente = None
        self.temps_precedent = None
        self.joueur_actuel = 1
        self.points_j1 = 0
        self.points_j2 = 0
        self.en_placement_apres_faute = False
        self.faute = False
        self.billes_tombees_tour = []
        self.canevas = None
        self.creer_canevas()
        self.menu_frame = None
        self.btn_pause = None
        self.after_id = None
        self.en_pause = False

    def creer_canevas(self):
        self.canevas = tk.Canvas(self.racine, width=self.largeur, height=self.hauteur)
        self.canevas.pack()
        for i in range(0, self.hauteur, 5):
            ratio = i / self.hauteur
            r, g, b = 11, 77, 34
            r = int(r + (50 * ratio))
            g = int(g + (30 * ratio))
            b = int(b + (10 * ratio))
            couleur = f'#{r:02x}{g:02x}{b:02x}'
            self.canevas.create_rectangle(0, i, self.largeur, i+5, fill=couleur, outline=couleur)
        self.canevas.create_rectangle(
            self.marge + 10, self.marge + 10,
            self.largeur - self.marge + 10, self.hauteur - self.marge + 10,
            fill="black", outline="", width=0
        )
        self.canevas.create_rectangle(
            self.marge, self.marge,
            self.largeur - self.marge, self.hauteur - self.marge,
            outline="#654321", width=12, fill="#1B4D3E"
        )
        ligne_placement = self.marge + 3/4 * (self.largeur - 2 * self.marge)
        self.canevas.create_line(
            ligne_placement, self.marge,
            ligne_placement, self.hauteur - self.marge,
            fill="white", width=10
        )

    def creer_trous(self):
        decalage = 10
        positions = [
            (self.marge + decalage, self.marge + decalage),
            (self.largeur - self.marge - decalage, self.marge + decalage),
            (self.marge + decalage, self.hauteur - self.marge - decalage),
            (self.largeur - self.marge - decalage, self.hauteur - self.marge - decalage)
        ]
        for x, y in positions:
            self.canevas.create_oval(
                x - self.rayon_bille*2, y - self.rayon_bille*2,
                x + self.rayon_bille*2, y + self.rayon_bille*2,
                fill="#777777", outline="#EEEEEE", width=2
            )
            self.canevas.create_oval(
                x - self.rayon_bille*1.5, y - self.rayon_bille*1.5,
                x + self.rayon_bille*1.5, y + self.rayon_bille*1.5,
                fill="black", outline=""
            )
            if positions.index((x, y)) == 0:
                tx, ty = x + self.rayon_bille*1.5, y + self.rayon_bille*1.5
            elif positions.index((x, y)) == 1:
                tx, ty = x - self.rayon_bille*1.5, y + self.rayon_bille*1.5
            elif positions.index((x, y)) == 2:
                tx, ty = x + self.rayon_bille*1.5, y - self.rayon_bille*1.5
            else:
                tx, ty = x - self.rayon_bille*1.5, y - self.rayon_bille*1.5
            self.trous.append((tx, ty))

    def creer_billes_depart(self):
        couleurs = ["red", "blue", "green", "yellow", "black", "orange"]
        x_depart, y_depart = 500, 400
        espacement = self.rayon_bille * 2 + 2
        k = 0
        for i in range(1, 6):
            for j in range(i):
                y = y_depart + (j - (i - 1) / 2) * espacement
                x = x_depart - (i - 1) * espacement
                if k < len(couleurs):
                    bille = Bille(self.canevas, k, x, y, self.rayon_bille, couleurs[k])
                    self.billes.append(bille)
                    k += 1

    def creer_interface(self):
        self.canevas.create_rectangle(
            190, 10, 410, 80,
            fill="#2C3E50", outline="#34495E", width=3
        )
        self.label_score = tk.Label(
            self.canevas, text='', bg='#2C3E50', fg='white',
            font=("Arial", 16, "bold"), bd=0, highlightthickness=3, highlightbackground="#34495E", highlightcolor="#34495E"
        )
        self.label_score.place(x=500, y=20)
        self.label_tour = tk.Label(
            self.canevas, text='', bg='#2C3E50', fg='white',
            font=("Arial", 16, "bold"), bd=0, highlightthickness=0
        )
        self.label_tour.place(x=200, y=20)
        self.indicateur_j1 = self.canevas.create_text(
            200, 60, text="◉", fill="yellow",
            font=("Arial", 20), anchor="w"
        )
        self.indicateur_j2 = self.canevas.create_text(
            380, 60, text="◉", fill="white",
            font=("Arial", 20), anchor="w"
        )
        self.canevas.create_text(
            800, 40, text="Billes tombées:",
            fill="white", font=("Arial", 12), anchor="w"
        )
        self.btn_pause = tk.Button(
            self.canevas, text="⏸ Pause", command=self.pause_game,
            bg="#F39C12", fg="white", font=("Arial", 12), bd=0
        )
        self.btn_pause.place(x=10, y=10)

    def commencer(self):
        self.creer_menu_principal()
        self.racine.mainloop()

    def creer_menu_principal(self):
        self.menu_frame = tk.Frame(self.racine, bg="#1B4D3E")
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        titre = tk.Label(self.menu_frame, text="Jeu de Billard", font=("Arial", 30, "bold"), fg="white", bg="#1B4D3E")
        titre.pack(pady=20)

        btn_jouer = tk.Button(self.menu_frame, text="Jouer", width=20, height=2,
                              command=self.lancer_partie, bg="#2ECC71", fg="white", font=("Arial", 14))
        btn_jouer.pack(pady=10)

        btn_quitter = tk.Button(self.menu_frame, text="Quitter", width=20, height=2,
                                command=self.racine.destroy, bg="#E74C3C", fg="white", font=("Arial", 14))
        btn_quitter.pack(pady=10)

    def lancer_partie(self):
        self.menu_frame.destroy()
        self.canevas.pack()
        self.creer_billes_depart()
        self.creer_interface()
        self.creer_trous()
        self.canevas.bind("<Button-1>", self.placer_bille_blanche)
        self.mettre_a_jour_infos_en_boucle()

    def placer_bille_blanche(self, event):
        ligne_placement = self.marge + 3/4 * (self.largeur - 2 * self.marge)
        if self.en_placement_apres_faute or event.x > ligne_placement:
            self.bille_blanche = Bille(self.canevas, -1, event.x, event.y, self.rayon_bille, "white")
            self.billes.append(self.bille_blanche)
            self.canne = Canne(self.canevas, self.bille_blanche, self.joueur_actuel)
            self.configurer_controles()
            self.en_placement_apres_faute = False
        else:
            self.canne = Canne(self.canevas, self.bille_blanche, self.joueur_actuel)

    def configurer_controles(self):
        self.canevas.unbind("<Button-1>")
        self.canne.dessiner()
        self.canevas.focus_set()
        self.racine.bind("<Left>", lambda _: self.canne.tourner_gauche())
        self.racine.bind("<KeyRelease-Left>", lambda _: self.canne.raz())
        self.racine.bind("<Right>", lambda _: self.canne.tourner_droite())
        self.racine.bind("<KeyRelease-Right>", lambda _: self.canne.raz())
        self.racine.bind("<Up>", lambda _: self.canne.ajuster_puissance(1))
        self.racine.bind("<Down>", lambda _: self.canne.ajuster_puissance(-1))
        self.racine.bind("<Return>", self.valider_angle)
        self.racine.bind("<space>", self.tirer)

    def valider_angle(self, _):
        self.racine.unbind("<Left>")
        self.racine.unbind("<Right>")
        self.racine.unbind("<Return>")

    def tirer(self, event):
        self.racine.unbind("<Shift_R>")
        self.racine.unbind("<Up>")
        self.racine.unbind("<Down>")
        self.racine.unbind("<space>")
        self.valider_angle(event)
        self.canevas.delete(self.canne.id)
        self.canevas.delete(self.canne.id_shadow)
        self.canevas.delete(self.canne.proj_id)
        angle_rad = math.radians(self.canne.angle)
        energie_cinetique = 0.5 * self.canne.poids * self.canne.puissance ** 2
        self.bille_blanche.vx = -energie_cinetique * math.sin(angle_rad) / 100
        self.bille_blanche.vy = energie_cinetique * math.cos(angle_rad) / 100
        self.mettre_a_jour_physique()

    def mettre_a_jour_physique(self):
        en_mouvement = False
        billes_a_supprimer = []
        
        for bille in self.billes:
            bille.vx *= 0.99
            bille.vy *= 0.99
            nouvelle_x = bille.x + bille.vx
            nouvelle_y = bille.y + bille.vy
            
            vx, vy = self.verifier_collision(bille, bille.vx, bille.vy)
            bille.vx, bille.vy = vx, vy
            
            # Vérifier si la bille doit être supprimée
            if bille.dans_trou:
                billes_a_supprimer.append(bille)
                continue  # Ne pas mettre à jour la position
            
            if bille in self.billes:
                bille.mettre_a_jour_position(nouvelle_x, nouvelle_y)
                if abs(bille.vx) > 1 or abs(bille.vy) > 1:
                    en_mouvement = True
        
        # Supprimer les billes tombées dans les trous
        for bille in billes_a_supprimer:
            self.gestion_bille_tombee(bille)
        
        self.verifier_collisions_billes()
        
        if en_mouvement and not self.en_pause:
            self.after_id = self.racine.after(20, self.mettre_a_jour_physique)
        else:
            if not self.faute and len(self.billes_tombees_tour) == 0:
                self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
            self.billes_tombees_tour = []
            self.faute = False
            for bille in self.billes:
                bille.vx = 0.0
                bille.vy = 0.0
                bille.dans_trou = False  # Réinitialiser le drapeau
            if self.bille_blanche and self.bille_blanche in self.billes:
                self.canne = Canne(self.canevas, self.bille_blanche, self.joueur_actuel)
                self.configurer_controles()

    def verifier_collision(self, bille, vx, vy):
        x1 = bille.x - bille.rayon
        y1 = bille.y - bille.rayon
        x2 = bille.x + bille.rayon
        y2 = bille.y + bille.rayon
        
        # Collisions avec les murs
        if x1 <= self.marge:
            vx = abs(vx)
        elif x2 >= self.largeur - self.marge:
            vx = -abs(vx)
        if y1 <= self.marge:
            vy = abs(vy)
        elif y2 >= self.hauteur - self.marge:
            vy = -abs(vy)
        
        # Collisions avec les trous
        for tx, ty in self.trous:
            distance = math.hypot(bille.x - tx, bille.y - ty)
            if distance < self.rayon_bille * 1.5:
                bille.dans_trou = True
                break
        
        return vx, vy

    def gestion_bille_tombee(self, bille):
        """Gère une bille tombée dans un trou"""
        self.canevas.delete(bille.id)
        self.canevas.delete(bille.text_id)
        self.canevas.delete(bille.shadow_id)
        
        if bille == self.bille_blanche:
            self.billes.remove(bille)
            self.bille_blanche = None
            self.faute = True
            self.joueur_actuel = 2 if self.joueur_actuel == 1 else 1
            self.en_placement_apres_faute = True
            self.show_custom_message('Info', f"Joueur {self.joueur_actuel}, placez la bille blanche")
            self.canevas.bind("<Button-1>", self.placer_bille_blanche)
            
        elif bille.couleur == "black":
            billes_restantes = [b for b in self.billes if b != self.bille_blanche and b.couleur != "black"]
            if len(billes_restantes) == 0:
                self.show_custom_message("Victoire", f"Joueur {self.joueur_actuel} gagne !")
            else:
                self.show_custom_message("Défaite", f"Joueur {self.joueur_actuel} perd !")
            time.sleep(2)
            self.racine.destroy()
            
        else:
            if self.joueur_actuel == 1:
                self.points_j1 += 1
            else:
                self.points_j2 += 1
            self.billes_tombees_tour.append(bille)
            self.billes.remove(bille)
            self.billes_tombees.append(bille)
            
            xdep = 925
            ydep = 40
            self.canevas.delete("billes_tombees")
            for i, b in enumerate(self.billes_tombees):
                self.canevas.create_oval(
                    xdep + i*30 - self.rayon_bille,
                    ydep - self.rayon_bille,
                    xdep + i*30 + self.rayon_bille,
                    ydep + self.rayon_bille,
                    fill=b.couleur,
                    tags="billes_tombees"
                )

    def verifier_collisions_billes(self):
        for i in range(len(self.billes)):
            b1 = self.billes[i]
            for j in range(i + 1, len(self.billes)):
                b2 = self.billes[j]
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                distance = math.hypot(dx, dy)
                distance_min = b1.rayon + b2.rayon
                if distance < distance_min:
                    nx = dx / distance
                    ny = dy / distance
                    dvx = b2.vx - b1.vx
                    dvy = b2.vy - b1.vy
                    produit_scalaire = dvx * nx + dvy * ny
                    if produit_scalaire > 0:
                        continue
                    e = 1.0
                    j = -(1 + e) * produit_scalaire / (2)
                    b1.vx -= j * nx
                    b1.vy -= j * ny
                    b2.vx += j * nx
                    b2.vy += j * ny

    def mettre_a_jour_infos_en_boucle(self):
        texte_info = f'Points J1: {self.points_j1} | Points J2: {self.points_j2}'
        self.label_score.config(text=texte_info)
        self.label_score.place(x=450, y=10)
        self.label_tour.config(text=f'Joueur 1 | Joueur 2')        
        couleur_j1 = "yellow" if self.joueur_actuel == 1 else "white"
        couleur_j2 = "yellow" if self.joueur_actuel == 2 else "white"
        self.canevas.itemconfig(self.indicateur_j1, fill=couleur_j1)
        self.canevas.itemconfig(self.indicateur_j2, fill=couleur_j2)
        self.racine.after(100, self.mettre_a_jour_infos_en_boucle)

    def show_custom_message(self, title, message):
        popup = tk.Toplevel(self.racine)
        popup.title(title)
        popup.geometry("300x150")
        popup.resizable(False, False)
        canvas = tk.Canvas(popup, width=300, height=150)
        canvas.pack()
        for i in range(150):
            couleur = f'#{50+i:02x}{50+i:02x}{255:02x}'
            canvas.create_rectangle(0, i, 300, i+1, fill=couleur, outline="")
        canvas.create_text(
            150, 50, text=message,
            fill="white", font=("Arial", 14)
        )
        btn = tk.Button(
            popup, text="OK", command=popup.destroy,
            bg="#34495E", fg="white", font=("Arial", 12),
            relief="flat", bd=0
        )
        btn.place(x=120, y=100)

    def pause_game(self):
        self.en_pause = not self.en_pause
        if self.en_pause:
            self.btn_pause.config(text="▶ Reprendre")
            if self.after_id:
                self.racine.after_cancel(self.after_id)
        else:
            self.btn_pause.config(text="⏸ Pause")
            self.mettre_a_jour_physique()

if __name__ == "__main__":
    jeu = JeuDeBillard()
    jeu.commencer()
