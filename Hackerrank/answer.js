Given an array of integers, calculate the ratios of its elements that are positive, negative, and zero.
Print the decimal value of each fraction on a new line with  places after the decimal.

Note: This challenge introduces precision problems. The test cases are scaled to six decimal places, though answers with absolute error of up to  are acceptable.
Complete the plusMinus function in the editor below.

plusMinus has the following parameter(s):

int arr[n]: an array of integers
Print
Print the ratios of positive, negative and zero values in the array. Each value should be printed on a separate line with  digits after the decimal. The function should not return a value.

Answer:
function plusMinus(arr) {
    // Write your code here
    let neg_count = 0;
    let pos_count = 0;
    let zero_count = 0;

    for(var x=0; x<arr.length; x++)
    {
        if(arr[x] < 0)
        {
            neg_count += 1;
        }
        else if(arr[x] == 0)
        {
            zero_count += 1;
        }
        else
        {
            pos_count += 1;
        }
    }
    console.log((pos_count/arr.length).toFixed(6));
    console.log((neg_count/arr.length).toFixed(6));
    console.log((zero_count/arr.length).toFixed(6));
}


A queue is an abstract data type that maintains the order in which elements were added to it, allowing the oldest elements to be removed from the front and new elements to be added to the rear. This is called a First-In-First-Out (FIFO) data structure because the first element added to the queue (i.e., the one that has been waiting the longest) is always the first one to be removed.

A basic queue has the following operations:

Enqueue: add a new element to the end of the queue.
Dequeue: remove the element from the front of the queue and return it.
In this challenge, you must first implement a queue using two stacks. Then process  queries, where each query is one of the following  types:

1 x: Enqueue element  into the end of the queue.
2: Dequeue the element at the front of the queue.
3: Print the element at the front of the queue.

Answer:
function processData(input)
{
    //Enter your code here
    this.item = [];

    var command = input.split(/\r?\n/);

    for(let x=0; x<command.length; x++)
    {
        if(/\s/.test(command[x]))
        {
            let c = command[x].split(/\s/);
            this.item.push(c[1]);
        }
        else
        {
            if(command[x] == '2')
            {
                this.item.splice(0,1);
            }
            else if(command[x] == '3')
            {
                console.log(this.item[0]);
            }
            else
            {
                let q = command[x];
            }
        }

    }

}


Complete the  function in the editor below, which has  parameter: a pointer to the root of a binary tree. It must print the values in the tree's preorder traversal as a single line of space-separated values.

Input Format

Our test code passes the root node of a binary tree to the preOrder function.

Constraints

 Nodes in the tree

Output Format

Print the tree's preorder traversal as a single line of space-separated values.

Ans:
var check_left = [];
var x = "";

function preOrder(root)
{
	if(root.data != null)
    {
        //print out the current node data
        process.stdout.write(root.data + " ");

        //check if left is empty
        if(root.left != null && root.right == null)
        {
            preOrder(root.left);
        }
        else if(root.left == null && root.right != null)
        {
            preOrder(root.right);
        }
        else if(root.left != null && root.right != null)
        {
            preOrder(root.left);
            preOrder(root.right);
        }
    }
    else
    {
        console.log("");
    }
    //console.log(root.left);
    //console.log(root.right);
}



Given pointers to the heads of two sorted linked lists, merge them into a single, sorted linked list. Either head pointer may be null meaning that the corresponding list is empty.
Example
 refers to
 refers to

The new list is
Function Description
Complete the mergeLists function in the editor below.
mergeLists has the following parameters:

SinglyLinkedListNode pointer headA: a reference to the head of a list
SinglyLinkedListNode pointer headB: a reference to the head of a list
Returns

SinglyLinkedListNode pointer: a reference to the head of the merged list
Input Format
The first line contains an integer , the number of test cases.
The format for each test case is as follows:
The first line contains an integer , the length of the first linked list.
The next  lines contain an integer each, the elements of the linked list.
The next line contains an integer , the length of the second linked list.
The next  lines contain an integer each, the elements of the second linked list.

Answer:
function mergeLists(head1, head2)
{
    if(head1 == null)
    {
        return head2;
    }
    else if(head2 == null)
    {
        return head1;
    }
    else if(head1.data < head2.data)
    {
        head1.next = mergeLists(head1.next, head2);
        return head1;
    }
    else
    {
        head2.next = mergeLists(head1, head2.next);
        return head2;
    }
}



A queue is an abstract data type that maintains the order in which elements were added to it, allowing the oldest elements to be removed from the front and new elements to be added to the rear. This is called a First-In-First-Out (FIFO) data structure because the first element added to the queue (i.e., the one that has been waiting the longest) is always the first one to be removed.

A basic queue has the following operations:

Enqueue: add a new element to the end of the queue.
Dequeue: remove the element from the front of the queue and return it.
In this challenge, you must first implement a queue using two stacks. Then process  queries, where each query is one of the following  types:

1 x: Enqueue element  into the end of the queue.
2: Dequeue the element at the front of the queue.
3: Print the element at the front of the queue.
Input Format

The first line contains a single integer, , denoting the number of queries.
Each line  of the  subsequent lines contains a single query in the form described in the problem statement above. All three queries start with an integer denoting the query , but only query  is followed by an additional space-separated value, , denoting the value to be enqueued.

function processData(input)
{
    //Enter your code here
    this.item = [];

    var command = input.split(/\r?\n/);

    for(let x=0; x<command.length; x++)
    {
        if(/\s/.test(command[x]))
        {
            let c = command[x].split(/\s/);
            this.item.push(c[1]);
        }
        else
        {
            if(command[x] == '2')
            {
                this.item.splice(0,1);
            }
            else if(command[x] == '3')
            {
                console.log(this.item[0]);
            }
            else
            {
                let q = command[x];
            }
        }

    }

} 
