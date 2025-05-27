#!/bin/bash

cpptraj -i combine_dcd.in
cpptraj -i get_frames.in

cp combine_dcd.in ../eq_2
cd ../eq_2
cpptraj -i combine_dcd.in
