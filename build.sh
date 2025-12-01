docker build -t langgraph:1.0.0 .;
docker save -o ./base_image/langgraph.tar langgraph:1.0.0;
rm ./base_image/langgraph.tar_part*;
split -b 90M ./base_image/langgraph.tar ./base_image/langgraph.tar_part_
rm ./base_image/langgraph.tar;
