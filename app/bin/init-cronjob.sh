#write out current crontab
crontab -l > mycron
x=$(pwd)
#echo new cron into cron file
echo "0,30 * * * * $x/app/bin/run-report-sync.sh" >> mycron
#install new cron file
crontab mycron
rm mycron