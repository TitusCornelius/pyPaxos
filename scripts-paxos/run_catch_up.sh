#!/bin/bash

projdir="$1"
conf=`pwd`/paxos.conf
n="$2"

if [[ x$projdir == "x" || x$n == "x" ]]; then
	echo "Usage: $0 <project dir> <number of values per proposer>"
    exit 1
fi

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM exit

./generate.sh $n > prop1
./generate.sh $n > prop2

echo "starting acceptors..."

$projdir/acceptor.sh 1 $conf &
$projdir/acceptor.sh 2 $conf &
$projdir/acceptor.sh 3 $conf &

sleep .5
echo "starting learner 1..."

$projdir/learner.sh 1 $conf > learn1 &

sleep .5
echo "starting proposers..."

$projdir/proposer.sh 1 $conf &
$projdir/proposer.sh 2 $conf &

sleep .5
echo "starting client 1..."

$projdir/client.sh 1 $conf < prop1 &

sleep .5
echo "starting learner 2..."
$projdir/learner.sh 2 $conf > learn2 &

sleep .5
echo "starting client 2..."

$projdir/client.sh 2 $conf < prop2 &

sleep 5

./check_all.sh

wait
