import inquirer

questions = [
	inquirer.Text("server_base_url", message="Enter the base url of your plex server:"),
	inquirer.Text("server_token", message="Todo"),
	inquirer.Path('library_dir', 'Where should we store your local song library?', normalize_to_absolute_path=True)
]

answers = inquirer.prompt(questions)

print(answers)
