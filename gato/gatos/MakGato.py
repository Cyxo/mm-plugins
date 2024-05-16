from random import random, randint

from ABaseGato import ABaseGato, require_alive

class MakGato(ABaseGato):
    """
        >Fav Food:
        >During deployment, increases all allies mood by 20 and when own mood reaches 75%,
        >immediately stops all allies stat(s) consumption for 45 minutes (has a cooldown of 2 hours). 
        >While hunting, every 10 minutes Mak has a base chance (15%) of finding food to restore all your allies
        >hunger by 10% and increase the mood of all allies by 10.
        >e1 -> e5:  increases the chance of finding food by 2% each (25% at e6)
        >e6: food found now increases mood by 20
    """

    # Override constants
    IMAGE = "https://catjam-united.s-ul.eu/1I8uBOPF"
    # ANIMATIONS = "mooncake"
    DISPLAY_NAME = "Tropical Sunset"
    RARITY = 5
    
    VALUES_TO_SAVE = ABaseGato.VALUES_TO_SAVE + [
        "buff_duration",
        "buff_cooldown",
        "find_food_cooldown"
    ]

    MAK_FOOD_EVENT_TYPE = "MAK_find_food"
    MAK_MOOD_EVENT_TYPE = "MAK_deploy_mood"
    MAK_CONSUMPTION_BUFF_EVENT_TYPE = "MAK_consumption_buff"
    EVENT_DESCRIPTIONS = ABaseGato.EVENT_DESCRIPTIONS | {
        MAK_CONSUMPTION_BUFF_EVENT_TYPE: "Stopped Stat consumption for all the team (x{count})",
        MAK_MOOD_EVENT_TYPE: "increased the mood of the team!",
        MAK_FOOD_EVENT_TYPE: "Found some food!! mood and hunger for all gatos increased (x{count})"
    }

    MAK_CONSUMPTION_BUFF_KEY: str = "MAK_consumption_buff"       # key for the stat consumption buff

    # Custom variables used for this gato
    buff_duration: int = 0              # Remaining duration for its buff
    buff_cooldown: int = 0              # Remaining cooldown until its buff can be triggered again
    find_food_cooldown: int = 0       # Remaining cooldown until it can find a rare object again

    def maybe_find_food(self, seconds) -> bool:
        """
        Returns False if can't use or didn't find
        Returns True if found food
        has a 15% chance to get food
        +2% more per eidolon 
        """

        found_food = False

        # Tick down cd if needed
        if self.find_food_cooldown > 0:
            self.find_food_cooldown = max(self.find_food_cooldown - seconds, 0)

        if self.find_food_cooldown > 0:
            return found_food

        eidolon_chance = 2*min(self.eidolon, 5)

        attempt = randint(1, 100)  # Random number between 1 and 100 for 1% granularity
        if attempt <= 15+eidolon_chance:  # 15% + 2per eidolon chance
            found_food = True
        self.find_food_cooldown = 600
        return found_food

    def maybe_buff(self,seconds) -> bool:
        """
            Takes care of buff cd 
        """
        #tick down cd
        apply_buff = False

        if self.buff_cooldown > 0 :
            self.buff_cooldown = max(self.buff_cooldown - seconds, 0)

        if self.buff_cooldown > 0:
            return  apply_buff
        
        if self.mood >= 75:
            self.buff_cooldown = 7200
            self.buff_duration = 2700
            apply_buff = True
        

    def maybe_remove_buff(self, seconds) -> bool:
        remove_buff = False
        
        if self.buff_duration > 0 :
            self.buff_duration = max(self.buff_duration - seconds, 0)

        if self.buff_duration > 0 :
            return  remove_buff



    def simulate(self, team: list["ABaseGato"], seconds: int = 1):
        # Food Hunt! 
        if self.maybe_find_food(seconds):
            for gato in team: 
                gato.add_mood(10)
                if self.eidolon == 6:
                    gato.add_mood(10)
                gato.add_hunger(10)

        #Deploy Mood
        if self.MAK_MOOD_EVENT_TYPE not in self._events:
            for gato in team:
                gato.add_mood(20)
            self._events.append({self.MAK_MOOD_EVENT_TYPE: None})

        #CONSUMPTION BUFF
        if self.maybe_buff(seconds) :
            for gato in team:
                if self.MAK_CONSUMPTION_BUFF_KEY not in gato.energy_loss_reductions:
                    gato.energy_loss_reductions[self.MAK_CONSUMPTION_BUFF_KEY] = 1

                if self.MAK_CONSUMPTION_BUFF_KEY not in gato.mood_loss_reductions:
                    gato.mood_loss_reductions[self.MAK_CONSUMPTION_BUFF_KEY] = 1

                if self.MAK_CONSUMPTION_BUFF_KEY not in gato.hunger_reductions:
                    gato.hunger_reductions[self.MAK_CONSUMPTION_BUFF_KEY] = 1
            
            self._events.append({self.MAK_CONSUMPTION_BUFF_EVENT_TYPE: None})

        if self.maybe_remove_buff(seconds):
             for gato in team:
            # Remove entries from energy_loss_reductions dictionary
                if self.MAK_CONSUMPTION_BUFF_KEY in gato.energy_loss_reductions:
                    del gato.energy_loss_reductions[self.MAK_CONSUMPTION_BUFF_KEY]

                # Remove entries from mood_loss_reductions dictionary
                if self.MAK_CONSUMPTION_BUFF_KEY in gato.mood_loss_reductions:
                    del gato.mood_loss_reductions[self.MAK_CONSUMPTION_BUFF_KEY]

                # Remove entries from hunger_reductions dictionary
                if self.MAK_CONSUMPTION_BUFF_KEY in gato.hunger_reductions:
                    del gato.hunger_reductions[self.MAK_CONSUMPTION_BUFF_KEY]


        # Then call the parent simulation (VERY IMPORTANT)
        super().simulate(seconds)
