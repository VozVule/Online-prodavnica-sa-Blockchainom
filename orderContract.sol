// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OrderContract {
    address public buyer;
    address public courier;
    address public owner;
    uint256 public price;

    enum State {CREATED, PAYED, PICKED_UP, FINISHED}
    State public currentState;

    constructor(address _buyer, uint256 _price) {
        owner = msg.sender;
        buyer = _buyer;
        price = _price;
        currentState = State.CREATED;
    }

    function getBuyer() external view returns(address) {
        return buyer;
    }
    
    function getCourier() external view returns (address) {
        return courier;
    }

    function getOwner() external view returns (address) {
        return owner;
    }

    function getPrice() external view returns (uint256) {
        return price;
    }

    function getState() external view returns (State) {
        return currentState;
    }

    modifier onlyBuyer() {
        require(msg.sender == buyer, "Only the buyer can call this function");
        _;
    }

    modifier onlyCourier() {
        require(msg.sender == courier, "Only the courier can call this function");
        _;
    }

    function setCourier(address _courier) external {
        require(currentState == State.PAYED, "Order must be payed before being picked up");
        courier = _courier;
        currentState = State.PICKED_UP;
    }

    function pay() external payable onlyBuyer {
        require(currentState == State.CREATED, "The order has already been payed");
        require(msg.value == price, "The payement must be the exact same as the price");

        currentState = State.PAYED;
    }

    function delivered() external onlyBuyer() {
        require(currentState == State.PICKED_UP, "The order must be picked up by the courier to be delivered");
        currentState == State.FINISHED;

        uint256 ownerShare = (price * 80) / 100;
        uint256 courierShare = price - ownerShare;

        payable(owner).transfer(ownerShare);
        payable(courier).transfer(courierShare);
    }

}