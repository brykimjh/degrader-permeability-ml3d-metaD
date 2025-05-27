#!/bin/bash

cpptraj -i get_frames.in
cpptraj -i split_dcd.in

cp split_dcd.in ../eq_2
cd ../eq_2
cpptraj -i split_dcd.in
