import sublime, sublime_plugin, tempfile, os

class LuaScratchCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		settings = sublime.load_settings("LuaScratch.sublime-settings");

		executable = settings.get("executable");

		selection = self.view.sel()[0];
		selectedText = "";

		if selection.empty():
			selectedText = self.view.substr(sublime.Region(0, self.view.size()));
		else:
			selectedText = self.view.substr(selection);

		file = tempfile.NamedTemporaryFile(mode='w+t', delete=False);
		file.write(selectedText);
		file_name = file.name;
		file.close();

		self.view.window().run_command("exec", {"cmd":[executable, file_name]});

		#os.remove(file_name);
		#print("test")