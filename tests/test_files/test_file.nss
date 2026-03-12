create node --id 1 --property Name=Alice --property Age=25 --property Gender=F --property Height=160
create node --id 2 --property Name=Tom --property Age=30 --property Gender=M --property Height=175
create edge 1 2 --id 1 --property Name=Siblings
edit node --id 2 --property Age=40
filter `A || B || C`;
search `Name==Tom`