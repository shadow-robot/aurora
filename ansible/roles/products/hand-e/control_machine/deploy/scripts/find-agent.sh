for P in /tmp/ssh-*/agent.*
do
    if [ -O "$P" ] && [ -O "$(dirname "$P")" ]
    then
        L=$(SSH_AUTH_SOCK="$P" timeout 1s ssh-add -l > >(wc -l))
        case $? in
            0)
                echo "$L $P"
                ;;
            1)
                echo "0 $P"
                ;;
        esac
    fi &
done | sort -rn | if read N P
then
    echo "SSH_AUTH_SOCK='$P'; export SSH_AUTH_SOCK"
else
    ssh-agent
fi
