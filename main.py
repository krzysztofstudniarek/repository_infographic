import os, math, shutil, subprocess, cairo, datetime, calendar

from mako.template import Template

from dateutil.parser import parse

shortlog_command = ['git', '--no-pager', 'shortlog','--no-merges', '-s', '-n']
log_command = ['git', '--no-pager' ,'log', '--no-merges', '--pretty=format:%aD']
oldest_command = ['git', 'log', '--max-parents=0', 'HEAD', '--pretty=format:%aD']
files_command = ['git' ,'ls-files']

def generate_infographic(repository):

	popular_languages = [['cs', 'c#', 0], ['py', 'python', 0], ['cpp', 'c++', 0], ['js', 'javascript',0], ['html', 'html', 0], ['rb', 'ruby', 0]]


	width = 1000

	pc_height = int(round(width/2.75, 0))

	top_commiters = 50
	top_language = 350
	top_punchcard = pc_height/20 + 450
	top_commits_per_day = top_punchcard + 400
	
	commits = run_git_command(log_command).splitlines()
	oldest_commit_date = int(run_git_command(oldest_command)[12:16])
	num_of_years = int(datetime.date.today().year - oldest_commit_date) + 1
	
	if num_of_years > max_years_in_commit_graph :
		num_of_years = max_years_in_commit_graph

	# Calculate the relative distance
	distance = int(math.sqrt((width*pc_height)/270.5))

	# Round the distance to a number divisible by 2
	if distance % 2 == 1:
		distance -= 1

	max_range = (distance/2) ** 2

	# Good values for the relative position
	left = width/18 + 10  # The '+ 10' is to prevent text from overlapping 
	indicator_length = pc_height/20

	days = ['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun']
	hours = ['12am'] + [str(x) for x in xrange(1, 12)] + ['12pm'] + [str(x) for x in xrange(1, 12)]	

	height = 800 + num_of_years*150 + pc_height
	
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	cr = cairo.Context(surface)
	
	cr.set_source_rgb(1, 1, 1)
	cr.rectangle(0, 0, width, height)
	cr.fill()
	
	cr.set_source_rgb(0.1, 0.1, 0.1)
	
	leaders = run_git_command(shortlog_command).splitlines()
	
	cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(25)

	cr.move_to(25,top_commiters)
	cr.show_text("Top 10 commiters: ")
	
	cr.set_font_size(15)
	
	cr.set_line_width(1);
	
	i = 0
	
	max_commit_no = int(leaders[0].lstrip().split('\t')[0])
	
	for leader in leaders[0:10] :
		cr.move_to(25, top_commiters + 25 + i*20)
		cr.show_text(leader.lstrip().split('\t')[1])
		strip_length = int(leader.lstrip().split('\t')[0])*(width-300)/max_commit_no
		cr.rectangle(250, top_commiters + 20 + i*20, strip_length, 5);
		cr.stroke_preserve();
		cr.fill();
		i = i+1

	files = run_git_command(files_command).splitlines()
	
	for file in files :
		split = file.split('.')
		for language in popular_languages :
			if split[len(split)-1] == language[0] :
				language[2] += 1
	
	best_lang = ''
	num_of_files = 0
	
	for language in popular_languages :
		if language[2] > num_of_files :
			best_lang = language[1]
			num_of_files = language[2]

	cr.set_font_size(25)
	cr.move_to(25,top_language)
	cr.show_text("Repo Language: "+best_lang)
	
	cr.set_font_size(25)
	cr.move_to(25,top_punchcard - 50)
	cr.show_text("Punch card: ")
	
	cr.set_font_size(15)
			
	data_log = [[x.strip().split(',')[0], x.strip().split(' ')[4].split(':')[0]] for x in commits]
	
	
	stats = {}
	for d in days:
		stats[d] = {}
		for h in xrange(0, 24):
			stats[d][h] = 0

	total = 0
	for line in data_log:
		stats[ line[0] ][ int(line[1]) ] += 1
		total += 1
		
	all_values = []
	for d, hour_pair in stats.items():
		for h, value in hour_pair.items():
			all_values.append(value)
	max_value = max(all_values)
	final_data = []
	for d, hour_pair in stats.items():
		for h, value in hour_pair.items():
			final_data.append( [ get_length(int( float(stats[d][h]) / max_value * max_range ), distance, max_range), top_punchcard + (days.index(d) + 1) * distance, left + (h + 1) * distance ] )

	cr.move_to(left, top_punchcard )
	cr.rel_line_to(0, 8 * distance )
	cr.rel_line_to(25 * distance, 0)
	cr.stroke()

	x, y = left, top_punchcard
	for i in xrange(8):
		cr.move_to(x, y)
		cr.rel_line_to(-indicator_length, 0)
		cr.stroke()
		y += distance

	x += distance
	for i in xrange(25):
		cr.move_to(x, y)
		cr.rel_line_to(0, indicator_length)
		cr.stroke()
		x += distance

	x, y = (left - 5), (top_punchcard + distance)
	for i in xrange(7):
		x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(days[i])
		cr.move_to(x - indicator_length - width, y + height/2)
		cr.show_text(days[i])
		y += distance

	x, y = (left + distance), (top_punchcard + (7 + 1) * distance + 5)
	for i in xrange(24):
		x_bearing, y_bearing, width, height, x_advance, y_advance = cr.text_extents(hours[i])
		cr.move_to(x - width/2 - x_bearing, y + indicator_length + height)
		cr.show_text(hours[i])
		x += distance

	for each in final_data:
		x = each[2]
		y = each[1]
		length = each[0]
		clr = (1 - float(length * length) / max_range )
		cr.set_source_rgba (clr, clr, clr)
		cr.move_to(x, y)
		cr.arc(x, y, length, 0, 2 * math.pi)
		cr.fill()
	
	
	cr.set_source_rgba (0, 0, 0)
	cr.set_font_size(25)
	cr.move_to(25,top_commits_per_day)
	cr.show_text("Commits by day: ")
	
	cr.set_font_size(15)

	
	years = [0] * num_of_years
	for i in range (0, num_of_years) :
		years[i] = [0] * 366
		
	for commit in commits :
		date = parse(commit)
		if datetime.date.today().year - date.year >= max_years_in_commit_graph:
			break
		years[int(datetime.date.today().year - date.year)][date.timetuple().tm_yday-1] += 1
	
	return years
	
def get_commits_per_day():

	commits = run_git_command(log_command).splitlines()
	oldest_commit_date = int(run_git_command(oldest_command)[12:16])
	num_of_years = int(datetime.date.today().year - oldest_commit_date) + 1
	
	max_years_in_commit_graph = 5
	
	if num_of_years > max_years_in_commit_graph :
		num_of_years = max_years_in_commit_graph
		
	num_of_days = num_of_years*365

	data = [0]*num_of_days
	
	for commit in commits :
		date = parse(commit)
		if datetime.date.today().year - date.year >= max_years_in_commit_graph:
			break
		data[int(datetime.date.today().year - date.year)*365+date.timetuple().tm_yday-1] += 1
	
	labels = [""]*num_of_days
	for i in range(0,len(data)):
		if i%365 == 0 :
			labels[i] = datetime.date.today().year - i/365
			print labels[i]
	
	return labels, data
	
def run_git_command(command):
	p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = p.communicate()[0]
	return out
	
def get_length(nr, distance, max_range):
    if nr == 0:
        return 0
    for i in xrange(1, distance/2):
        if i*i <= nr and nr < (i+1)*(i+1):
            return i
    if nr == max_range:
        return distance/2-1	

def main():
	if os.system('git --version') == 0 :
		repositories = open('repos.txt')
		print repositories
		for repository in repositories :
			mytemplate = Template(filename='template.html')
			p = subprocess.Popen(['git', 'clone', repository], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p.communicate()
			catalogue = repository.split('/')[4].split('.')[0]
			os.chdir(catalogue)
			labels, data = get_commits_per_day()
			os.chdir('..')
			site = open(catalogue+'.html', 'w')
			site.write(mytemplate.render(name = catalogue, data = data, labels = labels))
			site.close()
			os.system('rm -rf '+catalogue)
	else : 
		print 'YOU SHOULD HAVE INSTALLED GIT BEFORE RUNNING THIS CODE'
	

	
if __name__ == "__main__":
    main()