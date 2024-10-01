process echo_function() {
    input:
    path x1
    path x2
    output
    path x2
    echo "$x1" > "$2"
}
