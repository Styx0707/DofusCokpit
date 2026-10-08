on(construct){
   while(true)
   {
      if(!(0x02574141 & 0x02574141))
      {
         if(!ord("\t"))
         {
            break;
         }
      }
      else
      {
         §§push("cellRenderer");
         §§push("DefaultCellRenderer");
      }
      set(§§pop(),§§pop());
      enabled = true;
      multipleSelection = false;
      break;
   }
   rowHeight = 20;
   styleName = "";
}
