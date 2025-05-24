import arcade, random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Wizard Invaders"

PLAYER_SCALING = 2
ENEMY_SCALING = 1.5
SPELL_SCALING = 1

class WizardGame(arcade.Window):
    def __init__(self):
        # Create game window
        self.current_state = "START"
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color((48, 10, 56))
        self.background_music = arcade.load_sound("sounds/hold_the_line.wav")
        self.music_player = self.background_music.play(volume = 0.5, loop = True)
        self.sound_wizard_shoot = arcade.load_sound("sounds/wizard_pew.wav")
        self.sound_enemy_shoot = arcade.load_sound("sounds/enemy_pew.wav")
        self.sound_wizard_destroyed = arcade.load_sound("sounds/destroyed.wav")
        self.sound_wizard_damage = arcade.load_sound("sounds/damage.wav")

        # Create variables to hold game sprites
        self.player_list = None
        self.spell_list = None
        self.enemy_list = None
        self.enemy_spell_list = None
        self.enemy_shoot_timer = 0
        self.player_health = 5
        self.game_over = False
        self.win = False
        self.total_enemies_spawned = 0
        self.total_enemies_defeated = 0
        self.max_enemies = 20



    def setup(self):
        # create player, spell list, and enemy list
        self.player_list = arcade.SpriteList()
        player = arcade.Sprite("images/wizard.png", PLAYER_SCALING)
        player.center_x = SCREEN_WIDTH // 2
        player.center_y = 50
        self.player_list.append(player)
        self.player_sprite = player

        self.spell_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.enemy_spell_list = arcade.SpriteList()
        self.enemy_shoot_timer = 0
        self.spawn_timer = 0
        self.win = False
        self.total_enemies_spawned = 0
        self.total_enemies_defeated = 0
        self.max_enemies = 20

        # Create enemies
        for x in range(100, 700, 175):
            if x % 200 == 0:
                enemy = arcade.Sprite("images/monster.png", ENEMY_SCALING)
            else:
                enemy = arcade.Sprite("images/monster2.png", ENEMY_SCALING)
            enemy.center_x = x
            enemy.center_y = 550
            enemy.change_y = -0.3
            self.enemy_list.append(enemy)
        
        self.hearts = arcade.SpriteList()
        for i in range(self.player_health):
            heart = arcade.Sprite("images/heart.png", 1.5)
            heart.center_x = 30 + i * 20
            heart.center_y = SCREEN_HEIGHT - 30
            self.hearts.append(heart)


    
    def on_draw(self):
        # Draw everything on the screen
        self.clear()

        if self.current_state == "START":
            arcade.draw_text("WIZARD INVADERS", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40, arcade.color.RED, 48, anchor_x = "center")
            arcade.draw_text("Press ENTER to Start", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20, arcade.color.RED, 24, anchor_x = "center")
            arcade.draw_text("← → to move SPACE to shoot", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 260, arcade.color.RED, 15, anchor_x = "center")
            return
        
        self.player_list.draw()
        self.spell_list.draw()
        self.enemy_list.draw()
        self.enemy_spell_list.draw()
        self.hearts.draw()
        
        if self.game_over and not self.win:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 48, anchor_x = "center", anchor_y = "center")
        if self.win:
            arcade.draw_text("YOU WIN!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.GOLD, 48, anchor_x = "center", anchor_y = "center")


    
    def on_key_press(self, key, modifiers):
        if self.current_state == "START" and key == arcade.key.ENTER:
            self.current_state = "GAME"
            self.setup()
            return

        # Move the wizard or shoot when keys are pressed (game not over)
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -5
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 5
        elif key == arcade.key.SPACE and not self.game_over:
            spell = arcade.Sprite("images/spell.png", SPELL_SCALING)
            wand_offset_x = 15
            wand_offset_y = 35
            spell.center_x = self.player_sprite.center_x + wand_offset_x
            spell.center_y = self.player_sprite.center_y + wand_offset_y
            spell.change_y = 5
            self.spell_list.append(spell)
            arcade.play_sound(self.sound_wizard_shoot)
        
        # Press ENTER to restart game (if game is over)
        if self.game_over and key == arcade.key.ENTER:
            self.setup()
            self.game_over = False
            self.win = False
            self.current_state = "GAME"
            self.player_health = 5
            self.hearts = arcade.SpriteList()
            for i in range(self.player_health):
                heart = arcade.Sprite("images/heart.png", 1.5)
                heart.center_x = 30 + i * 20
                heart.center_y = SCREEN_HEIGHT - 30
                self.hearts.append(heart)
            return
    


    def on_key_release(self, key, modifiers):
        # Stop moving when key is released
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0



    def on_update(self, delta_time):
        if self.current_state != "GAME":
            return

        # Move everything and check for collisions
        self.player_sprite.update()
        self.player_list.update()
        self.spell_list.update()
        # self.enemy_list.update()
        self.enemy_spell_list.update()

        # Make enemies disappear when hit
        for spell in self.spell_list:
            hit_list = arcade.check_for_collision_with_list(spell, self.enemy_list)
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                spell.remove_from_sprite_lists()
                self.total_enemies_defeated += 1
        
        # Enemy shooting logic
        if not self.game_over:
            self.enemy_list.update()
            self.enemy_shoot_timer += delta_time
            if self.enemy_shoot_timer > 1.0:
                enemy_list_as_list = list(self.enemy_list)
                shooters = random.sample(enemy_list_as_list, min(2, len(self.enemy_list)))
                for enemy in shooters:
                    spell = arcade.Sprite("images/enemy_spell.png", SPELL_SCALING)
                    spell.center_x = enemy.center_x
                    spell.center_y = enemy.center_y
                    spell.change_y = -5
                    self.enemy_spell_list.append(spell)
                    arcade.play_sound(self.sound_enemy_shoot)
                self.enemy_shoot_timer = 0
            
            for enemy in self.enemy_list:
                enemy.center_y -= 0.5

        # Spawn new enemy only if limit not reached
        self.spawn_timer += delta_time
        if self.spawn_timer > 2:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Check if player is hit
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_spell_list)
        for spell in hit_list:
            spell.remove_from_sprite_lists()
            if not self.game_over:
                self.player_health -= 1
                arcade.play_sound(self.sound_wizard_damage)
                if self.hearts:
                    self.hearts.pop()
                if self.player_health == 0:
                    self.game_over = True
                    arcade.play_sound(self.sound_wizard_destroyed, volume = 1.0)
                    self.player_sprite.remove_from_sprite_lists()
        
        # Check if enemy reaches the bottom of the screen
        for enemy in self.enemy_list:
            if enemy.center_y < 5:
                self.game_over = True
                self.player_sprite.remove_from_sprite_lists()
                break
        
        # Keep player on the screen
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        if self.player_sprite.right > SCREEN_WIDTH:
            self.player_sprite.right = SCREEN_WIDTH
        
        # If all enemies are defeated, the player wins
        if (not self.game_over and self.total_enemies_spawned == self.max_enemies and len(self.enemy_list) == 0):
            self.win = True
            self.game_over = True
            self.player_sprite.remove_from_sprite_lists()
        
        # Remove off-screen spells
        for spell in self.spell_list:
            if spell.top > SCREEN_HEIGHT:
                spell.remove_from_sprite_lists()
        
        for spell in self.enemy_spell_list:
            if spell.bottom < 0:
                spell.remove_from_sprite_lists()
    


    def spawn_enemy(self):
        if self.total_enemies_spawned >= self.max_enemies:
            return

        image = random.choice(["images/monster.png", "images/monster2.png"])
        enemy = arcade.Sprite(image, ENEMY_SCALING)
        enemy.center_x = random.randint(50, SCREEN_WIDTH - 50)
        enemy.center_y = SCREEN_HEIGHT + 40
        self.enemy_list.append(enemy)
        self.total_enemies_spawned += 1
        


def main():
    game = WizardGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()