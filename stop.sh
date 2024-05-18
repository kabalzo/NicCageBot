#!/bin/bash
read < pid.txt
kill $(($REPLY))
