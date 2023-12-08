import sqlite3

db_connection = sqlite3.connect('../db/anki.db', check_same_thread = False)
db_cursor = db_connection.cursor()

def get_deckID_by_name(user_ID, deck_name):
	db_cursor.execute(f'SELECT Id FROM Decks WHERE UserId="{user_ID}" AND Name="{deck_name}"')
	return db_cursor.fetchone()[0]

def get_available_decks_from_DB(user_ID):
	db_cursor.execute(f'SELECT Name FROM Decks WHERE UserId="{user_ID}"')
	decks = db_cursor.fetchall()
	return decks

def get_cards_from_deck(user_ID, deck_name):
	deck_ID = get_deckID_by_name(user_ID, deck_name)
	db_cursor.execute(f'SELECT * FROM Words WHERE DeckId="{deck_ID}"')
	words = db_cursor.fetchall()
	return words

def check_if_deck_exists(user_ID, message):
	res = db_cursor.execute(f'SELECT * FROM Decks WHERE (UserId="{user_ID}" AND Name="{message}")')
	return not (res.fetchone() is None)

def add_new_deck_to_DB(user_ID, deck_name):
	db_cursor.execute(f'INSERT INTO Decks (UserId, Name) VALUES ("{user_ID}", "{deck_name}")')
	db_connection.commit()

def add_new_card_to_DB(user_ID, deck_name, word, translation, date_to_repeat):
	deck_ID = get_deckID_by_name(user_ID, deck_name)
	db_cursor.execute(f'INSERT INTO Words (DeckId, Word, Translation, DateToRepeat) VALUES ({deck_ID}, "{word}", "{translation}", "{date_to_repeat}")')
	db_connection.commit()

def rename_deck(user_ID, deck_name, new_name):
	db_cursor.execute(f'UPDATE Decks SET Name="{new_name}" WHERE (UserId="{user_ID}" AND Name="{deck_name}")')
	db_connection.commit()

def delete_deck_from_DB(user_ID, deck_name):
	db_cursor.execute(f'DELETE FROM Words WHERE DeckId="{get_deckID_by_name(user_ID, deck_name)}"')
	db_cursor.execute(f'DELETE FROM Decks WHERE (UserId="{user_ID}" AND Name="{deck_name}")')
	db_connection.commit()

def edit_word_in_deck(user_ID, deck_name, old_word, old_translation, new_word, new_translation):
	db_cursor.execute(f'UPDATE Words SET Word="{new_word}", Translation="{new_translation}" WHERE (DeckId="{get_deckID_by_name(user_ID, deck_name)}" AND Word="{old_word}" AND Translation="{old_translation}")')
	db_connection.commit()

def delete_card_from_deck(card_ID):
	db_cursor.execute(f'DELETE FROM Words WHERE Id="{card_ID}"')
	db_connection.commit()

def update_word_repeat_date(word_ID, new_repeat_date, new_date_multiplier):
	db_cursor.execute(f'UPDATE Words SET DateToRepeat="{new_repeat_date}", DateMultiplier="{new_date_multiplier}" WHERE Id="{word_ID}"')
	db_connection.commit()