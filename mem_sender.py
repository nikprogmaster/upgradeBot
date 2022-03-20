import random


class MemSender:

    def __init__(self):
        self.participants = []
        self.group_number = 0
        self.game_id = self.get_random_id()

    def get_random_participant(self, parts):
        index = random.randrange(0, len(parts))
        participant = parts[index]
        parts.remove(parts[index])
        return participant

    def get_correct_group_number(self, mems_number):
        while len(self.participants) > mems_number * self.group_number:
            self.group_number += 1
        return self.group_number

    def send_memes(self, all_memes, bot):
        participants = self.participants.copy()
        memes = all_memes.copy()
        index = len(participants)
        while index > 0:
            parts_group = []
            step = self.get_correct_group_number(len(all_memes))
            if len(participants) < self.group_number:
                step = len(participants)
            for i in range(step):
                parts_group.append(self.get_random_participant(participants))
            mem_index = random.randrange(0, len(memes))
            mem_path = memes[mem_index]
            memes.remove(memes[mem_index])
            index -= step
            for i in parts_group:
                bot.send_photo(i, open(mem_path, 'rb'))

    def add_participant(self, participant):
        self.participants.append(participant)

    def get_random_id(self):
        return random.randrange(0, 9999)

    def get_correct_ending(self):
        o = len(self.participants) % 10
        if o == 1:
            return ' участник'
        elif o == 2 or o == 3 or o == 4:
            return ' участника'
        else:
            return ' участников'
