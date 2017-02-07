import os, math, shutil, subprocess, cairo, datetime, calendar

from dateutil.parser import parse

shortlog_command = ['git', '--no-pager', 'shortlog','--no-merges', '-s', '-n']
log_command = ['git', '--no-pager' ,'log', '--no-merges', '--pretty=format:%aD']
oldest_command = ['git', 'log', '--max-parents=0', 'HEAD', '--pretty=format:%aD']

width = 850


def get_leaders():
	p = subprocess.Popen(shortlog_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = p.communicate()[0]
	return out

def get_commits_by_date():
	p = subprocess.Popen(log_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = p.communicate()[0]
	return out
	
def get_oldest_commit():
	p = subprocess.Popen(oldest_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = p.communicate()[0]
	return out
	
def max_ln(buckets):
	minValue = len(buckets[0])
	for i in range(1, len(buckets)):
		if len(buckets[i]) < minValue:
			minValue = len(buckets[i])
	return minValue
	
def generate_infographic(repository):
	commits = get_commits_by_date().splitlines()
	oldest_commit_date = parse(get_oldest_commit())
	num_of_years = int(datetime.date.today().year - oldest_commit_date.year) + 1
	
	height = 400 + num_of_years*150

	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
	cr = cairo.Context(surface)
	
	cr.set_source_rgb(1, 1, 1)
	cr.rectangle(0, 0, width, height)
	cr.fill()
	
	cr.set_source_rgb(0.1, 0.1, 0.1)
        
	
	leaders = get_leaders().splitlines()
	
	cr.select_font_face("Purisa", cairo.FONT_SLANT_NORMAL,cairo.FONT_WEIGHT_NORMAL)
	cr.set_font_size(25)

	cr.move_to(25,50)
	cr.show_text("Top 10 commiters: ")
	
	cr.set_font_size(15)
	
	cr.set_line_width(1);
	
	i = 0
	
	for leader in leaders[0:10] :
		cr.move_to(25, 75 + i*20)
		cr.show_text(leader.lstrip().split('\t')[1])
		strip_length = int(leader.lstrip().split('\t')[0])
		cr.rectangle(250, 70 + i*20, strip_length, 5);
		cr.stroke_preserve();
		cr.fill();
		i = i+1
	
	cr.set_font_size(25)
	cr.move_to(25,300)
	cr.show_text("Commits by day: ")
	
	cr.set_font_size(15)

	commits = get_commits_by_date().splitlines()
	
	years = [0] * num_of_years
	for i in range (0, num_of_years) :
		years[i] = [0] * 366
	
	for commit in commits :
		date = parse(commit)
		years[int(datetime.date.today().year - date.year)][date.timetuple().tm_yday] += 1
	for i in range(0, len(years)) :
		x = 80
		for k in range(1,13) :
			cr.rectangle(x, 400 + 150*i , 2, 10)
			cr.stroke_preserve()
			x += 2*calendar.monthrange((datetime.date.today().year - i),k)[1]

		for j in range(0, len(years[i])) :
			cr.move_to(25,400 + 150*i)
			cr.show_text(str(datetime.date.today().year - i))
			cr.rectangle(j*2 + 80, 400 + 150*i - years[i][j]*5 , 2, years[i][j]*5)
			cr.stroke_preserve()

	surface.write_to_png('output.png')
	
def main():
	if os.system('git --version') == 0 :
		repositories = open('repos.txt')
		for repository in repositories :
			p = subprocess.Popen(['git', 'clone', repository], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p.communicate()
			catalogue = repository.split('/')[4].split('.')[0]
			os.chdir(catalogue)
			generate_infographic(repository)
			shutil.copyfile('output.png', '../out/'+catalogue+'.png')
			os.chdir('..')
			os.system('rm -rf '+catalogue)
	else : 
		print 'YOU SHOULD HAVE INSTALLED GIT BEFORE RUNNING THIS CODE'
	

	
if __name__ == "__main__":
    main()