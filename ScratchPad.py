import sublime, sublime_plugin, tempfile, os, re;

global g_current_file;
global g_last_view;
g_current_file = None;
g_last_view = None;


# Two methods that could be used here:

	# get language name
	# check if .sublime-build exists for language name
	# if it doesn't, somehow get the file extension
	# check for .sublime-build using file extension
		# wouldn't work if it's a scratch buffer

	# create temp file
	# change extension (just incase) of temp file to extension of running file
	# quickly switch to that file and run_command("build")
	# immediately after, run_command("close")

		# path = sublime.packages_path().split("\\");
		# path.pop();
		# path.append(view.settings().get('syntax'));

		# open("/".join(path).replace("tmLanguage", "sublime-build"));

		# re.search("<string>(\w+)</string>", open(os.path.join("\\".join(sublime.packages_path().split("\\")[:-1]), view.settings().get('syntax'))).read()).group(1)

class ScratchpadFile: # class to delegate the data to
	def __init__(self, file):
		self.file = file;
		self.file_name = file.name;

	def set_file(self, file):
		self.file = file;

	def unlink(self):
		try:
			os.unlink(self.file_name);
		except OSError, e:
			print("Couldn't remove file %s, %i, %s" % (self.file_name, e.errorno, e.strerror));


class ScratchpadCommand(sublime_plugin.TextCommand):
	def __get_filetype(self):
		syntaxpath = os.path.join( os.path.split( os.path.normcase(sublime.packages_path()) )[0], os.path.normcase(self.view.settings().get('syntax')) ); # obtain the absolute path to the syntax file
		# so now we have a path where the last 3 entries are: packages / syntax folder / syntax.tmlanguage
		# splitpath = syntaxpath.split(os.sep);


		text = None;
		with open(syntaxpath, "rt") as f:
			text = f.read(); # not sure how the fileTypes array can be implemented in the file, but we will just read the entire file for now

			if text != None:
				filetype = re.search("<key>.*(\n?).*<array>.*(\n?).*<string>(\w+)<\/string>", text).group(3); # hacky regex to find first filetype result

				return filetype;

			# name = re.search("", text); # another to get the name (py.sublime-build doesn't exist, but python.sublime-build does)

			# if os.path.exists(path):

			# elif os.path.exists():

			# syntax.sublime-build
			# name/syntax.sublime-build
			# name/name.sublime-build

	def __get_selection(self):
		selection = self.view.sel()[0]; # only the first selection, for now...
		selectedText = "";

		if selection.empty():
			selectedText = self.view.substr(sublime.Region(0, self.view.size())); # grab entire file
		else:
			selectedText = self.view.substr(selection); # grab just the selected text
		
		return selectedText;

	def run(self, edit):
		if self.view.sel()[0].empty() and not(self.view.is_dirty() or self.view.is_scratch()) and self.view.file_name() != None:
			self.view.window().run_command("build");
			return;

		global g_current_file;
		settings = sublime.load_settings("ScratchPad.sublime-settings");
		filetype = "." + self.__get_filetype();
		selectedText = self.__get_selection();
		new_view = None;

		with tempfile.NamedTemporaryFile(mode='w+t', delete=False, prefix="scratchpad", suffix=filetype) as f:
			f.write(selectedText);
			g_current_file = ScratchpadFile(f);
			new_view = self.view.window().open_file(f.name);

		global g_last_view;
		g_last_view = self.view;

class ScratchpadEvent(sublime_plugin.EventListener):
	def on_load(self, view):
		global g_current_file;
		if g_current_file != None and os.path.normcase(g_current_file.file_name) == os.path.normcase(view.file_name()):
			window = view.window();
			window.run_command("build");
			window.run_command("close");
			# g_current_file.unlink(); # build is an asynchronous call
			
			global g_last_view;
			if g_last_view != None and window.active_view() != g_last_view:
				window.focus_view(g_last_view);

			g_last_view = None;
			g_current_file = None;
