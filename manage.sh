

# Clear all migrations files for each app
clear_migrations() {
    
    for dir in $(ls); do
        migration_dir=$(ls $dir | grep -o "migrations")

        if ([ -z "$migration_dir" ]); then
            continue
        fi

        app_dir=$(echo $dir/$migration_dir)
    
        for file in $(ls $app_dir); do
            if ([ "$file" = "__init__.py" ]); then
                continue
            fi

            echo "Removing $app_dir/$file"

            if ([ "$file" = "__pycache__" ]); then
                rm  $app_dir/$file -rf
                continue
            fi

            rm $app_dir/$file
        done       
    done

    echo "✅ Cleared migrations successfully"
}


# Check if the first argument is clear-migrations or -cm
if ([ "$1" = "clear-migrations" ] || [ "$1" = "-cm" ]); then
    clear_migrations
else
    echo "❌ Invalid command. Please use clear-migrations or -cm"
fi