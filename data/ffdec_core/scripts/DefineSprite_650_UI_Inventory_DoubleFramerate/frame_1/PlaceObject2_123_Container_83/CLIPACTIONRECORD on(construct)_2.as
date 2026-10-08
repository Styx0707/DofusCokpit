on(construct){
   backgroundRenderer = "UI_InventoryContainerBackground";
   borderRenderer = "";
   dragAndDrop = true;
   enabled = true;
   highlightFront = true;
   if(dofus.Constants.DOUBLEFRAMERATE)
   {
      highlightRenderer = "UI_InventoryContainerHighlight_DoubleFramerate";
   }
   else
   {
      highlightRenderer = "UI_InventoryContainerHighlight";
   }
   margin = 2;
   showLabel = false;
   styleName = "default";
}
